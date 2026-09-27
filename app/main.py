from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session


from app.database.connection import Base, engine, get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.models.module import TrainingModule
from app.schemas.module import ModuleCreate
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate
from app.models.progress import LessonProgress
from app.schemas.progress import ProgressCreate
from app.models.question import QuizQuestion
from app.schemas.question import QuestionCreate,QuestionPublic
from app.schemas.quiz import QuizSubmission
from app.models.quiz_attempt import QuizAttempt
from app.models.drill import TrainingDrill
from app.schemas.drill import TrainingDrillCreate
from app.models.drill_progress import DrillProgress
from app.models.drill_question import DrillQuestion
from app.schemas.drill_progress import DrillProgressCreate
from app.schemas.drill_question import (
    DrillQuestionCreate,
    DrillQuizSubmission
)
from app.models.drill_quiz_attempt import DrillQuizAttempt
from app.models.certificate import Certificate
import uuid
import os
from dotenv import load_dotenv
import qrcode
from fastapi.responses import FileResponse
from app.models.lesson_translation import LessonTranslation
from app.schemas.lesson_translation import LessonTranslationCreate
from app.models.question_translation import QuestionTranslation
from app.schemas.question_translation import QuestionTranslationCreate
from app.models.drill_question_translation import DrillQuestionTranslation
from app.schemas.drill_question_translation import DrillQuestionTranslationCreate
from app.schemas.login import LoginRequest
from pwdlib import PasswordHash

import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security import get_current_user
from fastapi.middleware.cors import CORSMiddleware
import os



Base.metadata.create_all(bind=engine)

app = FastAPI()

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.8:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SIH Backend is running"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    return {"message": "Database connection working"}

password_hash = PasswordHash.recommended()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def admin_required(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "user_id": user_id,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    

@app.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(user_data.password)

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }





    


@app.get("/users")
def get_users(
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }
        for user in users
    ]
@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "User not found"}

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "User not found"}

    user.name = user_data.name
    user.email = user_data.email

    # Hash the new password
    user.password = password_hash.hash(user_data.password)

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "User not found"}

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

@app.post("/modules")
def create_module(
    module: ModuleCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    new_module = TrainingModule(
        title=module.title,
        description=module.description,
        difficulty=module.difficulty,
        language=module.language
    )

    db.add(new_module)
    db.commit()
    db.refresh(new_module)

    return new_module

@app.get("/modules")
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(TrainingModule).all()
    return modules

@app.get("/modules/{module_id}")
def get_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    return module

@app.post("/modules/{module_id}/lessons")
def create_lesson(
    module_id: int,
    lesson: LessonCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    new_lesson = Lesson(
        title=lesson.title,
        content=lesson.content,
        module_id=module_id
    )

    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson

@app.get("/modules/{module_id}/lessons")
def get_module_lessons(
    module_id: int,
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).all()

    return lessons
@app.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        return {"message": "Lesson not found"}

    return lesson

@app.post("/users/{user_id}/lessons/{lesson_id}/progress")
def update_progress(
    user_id: int,
    lesson_id: int,
    progress: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own progress"
        )

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        return {"message": "Lesson not found"}

    existing_progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()

    if existing_progress:
        existing_progress.completed = progress.completed
    else:
        existing_progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            completed=progress.completed
        )
        db.add(existing_progress)

    db.commit()
    db.refresh(existing_progress)

    return existing_progress

@app.get("/users/{user_id}/progress")
def get_user_progress(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own progress"
        )

    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id
    ).all()

    return progress

@app.get("/users/{user_id}/modules/{module_id}/progress")
def get_module_progress(
    user_id: int,
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own module progress"
        )

    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    total_lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).count()

    completed_lessons = (
        db.query(LessonProgress)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .filter(
            LessonProgress.user_id == current_user.id,
            Lesson.module_id == module_id,
            LessonProgress.completed == True
        )
        .count()
    )

    if total_lessons == 0:
        percentage = 0
    else:
        percentage = (completed_lessons / total_lessons) * 100

    return {
        "module_id": module_id,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percentage": percentage
    }

@app.get("/users/{user_id}/modules/{module_id}/completion")
def check_module_completion(
    user_id: int,
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only check your own module completion"
        )

    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    total_lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).count()

    completed_lessons = (
        db.query(LessonProgress)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .filter(
            LessonProgress.user_id == current_user.id,
            Lesson.module_id == module_id,
            LessonProgress.completed == True
        )
        .count()
    )

    completed = (
        total_lessons > 0
        and completed_lessons == total_lessons
    )

    return {
        "user_id": current_user.id,
        "module_id": module_id,
        "completed": completed,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons
    }

@app.get("/modules/{module_id}/summary")
def get_module_summary(
    module_id: int,
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    total_lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).count()

    return {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "difficulty": module.difficulty,
        "language": module.language,
        "total_lessons": total_lessons
    }

@app.post("/modules/{module_id}/questions")
def create_question(
    module_id: int,
    question: QuestionCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    new_question = QuizQuestion(
        module_id=module_id,
        question=question.question,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=question.correct_answer
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question

@app.get(
    "/modules/{module_id}/questions",
    response_model=list[QuestionPublic]
)
def get_module_questions(
    module_id: int,
    language: str = "en",
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return []

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.module_id == module_id
    ).all()

    result = []

    for question in questions:
        translation = db.query(QuestionTranslation).filter(
            QuestionTranslation.question_id == question.id,
            QuestionTranslation.language.ilike(language)
        ).first()

        if translation:
            result.append({
                "id": question.id,
                "module_id": question.module_id,
                "question": translation.question,
                "option_a": translation.option_a,
                "option_b": translation.option_b,
                "option_c": translation.option_c,
                "option_d": translation.option_d
            })
        else:
            result.append(question)

    return result

@app.post("/users/{user_id}/modules/{module_id}/quiz")
def submit_quiz(
    user_id: int,
    module_id: int,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Make sure the logged-in user matches the URL user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit a quiz for yourself"
        )

    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.module_id == module_id
    ).all()

    score = 0

    for question in questions:
        answer = submission.answers.get(question.id)

        if answer and answer.upper() == question.correct_answer.upper():
            score += 1

    total_questions = len(questions)

    percentage = (
        (score / total_questions) * 100
        if total_questions > 0
        else 0
    )

    attempt = QuizAttempt(
        user_id=current_user.id,
        module_id=module_id,
        score=score,
        total_questions=total_questions,
        percentage=percentage
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "user_id": current_user.id,
        "module_id": module_id,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage
    }

@app.get("/users/{user_id}/quiz-attempts")
def get_quiz_attempts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own quiz history"
        )

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).all()

    return attempts


@app.post("/users/{user_id}/modules/{module_id}/certificate")
def generate_certificate(
    user_id: int,
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -------------------------
    # USER ACCESS
    # -------------------------

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only generate your own certificate"
        )

    # -------------------------
    # CHECK USER
    # -------------------------

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -------------------------
    # CHECK MODULE
    # -------------------------

    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    # -------------------------
    # LESSON COMPLETION
    # -------------------------

    lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).all()

    total_lessons = len(lessons)

    if total_lessons == 0:
        raise HTTPException(
            status_code=400,
            detail="No lessons found for this module"
        )

    lesson_ids = [
        lesson.id
        for lesson in lessons
    ]

    completed_lessons = db.query(
        LessonProgress
    ).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_id.in_(lesson_ids),
        LessonProgress.completed == True
    ).count()

    if completed_lessons < total_lessons:
        return {
            "message": "Complete all lessons before getting the certificate",
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        }

    # -------------------------
    # DRILL COMPLETION
    # -------------------------

    drills = db.query(TrainingDrill).filter(
        TrainingDrill.module_id == module_id
    ).all()

    total_drills = len(drills)

    if total_drills > 0:

        drill_ids = [
            drill.id
            for drill in drills
        ]

        completed_drills = db.query(
            DrillProgress
        ).filter(
            DrillProgress.user_id == user_id,
            DrillProgress.drill_id.in_(drill_ids),
            DrillProgress.completed == True
        ).count()

        if completed_drills < total_drills:
            return {
                "message": "Complete all drills before getting the certificate",
                "completed_drills": completed_drills,
                "total_drills": total_drills
            }

        # -------------------------
        # DRILL QUIZ COMPLETION
        # -------------------------

        for drill in drills:

            latest_drill_quiz = db.query(
                DrillQuizAttempt
            ).filter(
                DrillQuizAttempt.user_id == user_id,
                DrillQuizAttempt.drill_id == drill.id
            ).order_by(
                DrillQuizAttempt.id.desc()
            ).first()

            if not latest_drill_quiz:
                return {
                    "message": "Complete all drill quizzes before getting the certificate",
                    "drill_id": drill.id
                }

            if not latest_drill_quiz.passed:
                return {
                    "message": "Pass all drill quizzes before getting the certificate",
                    "drill_id": drill.id,
                    "percentage": latest_drill_quiz.percentage,
                    "required_percentage": 70
                }

    # -------------------------
    # REGULAR MODULE QUIZ
    # -------------------------

    latest_attempt = db.query(
        QuizAttempt
    ).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.module_id == module_id
    ).order_by(
        QuizAttempt.id.desc()
    ).first()

    if not latest_attempt:
        return {
            "message": "Complete the quiz before getting the certificate"
        }

    if latest_attempt.percentage < 70:
        return {
            "message": "Quiz score is too low for certification",
            "score": latest_attempt.score,
            "total_questions": latest_attempt.total_questions,
            "percentage": latest_attempt.percentage,
            "required_percentage": 70
        }

    # -------------------------
    # CHECK EXISTING CERTIFICATE
    # -------------------------

    existing_certificate = db.query(
        Certificate
    ).filter(
        Certificate.user_id == user_id,
        Certificate.module_id == module_id
    ).first()

    if existing_certificate:
        return {
            "message": "Certificate already exists",
            "certificate_id": existing_certificate.id,
            "certificate_number": existing_certificate.certificate_number
        }

    # -------------------------
    # GENERATE CERTIFICATE
    # -------------------------

    certificate_number = (
        f"CERT-{uuid.uuid4().hex[:12].upper()}"
    )

    certificate = Certificate(
        user_id=user_id,
        module_id=module_id,
        certificate_number=certificate_number
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    # -------------------------
    # FINAL RESPONSE
    # -------------------------

    return {
        "message": "Certificate generated successfully",
        "certificate_id": certificate.id,
        "certificate_number": certificate.certificate_number,
        "user_id": user_id,
        "module_id": module_id,
        "quiz_percentage": latest_attempt.percentage,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "total_drills": total_drills,
        "certificate_eligibility": True
    }


@app.get("/certificates/{certificate_number}")
def verify_certificate(
    certificate_number: str,
    db: Session = Depends(get_db)
):
    certificate = db.query(Certificate).filter(
        Certificate.certificate_number == certificate_number
    ).first()

    if not certificate:
        return {
            "valid": False,
            "message": "Certificate not found"
        }

    user = db.query(User).filter(
        User.id == certificate.user_id
    ).first()

    module = db.query(TrainingModule).filter(
        TrainingModule.id == certificate.module_id
    ).first()

    return {
        "valid": True,
        "message": "Certificate is valid",
        "certificate_number": certificate.certificate_number,
        "user_id": user.id,
        "user_name": user.name,
        "module_id": module.id,
        "module_title": module.title
    }

@app.get("/certificates/{certificate_number}/qr")
def generate_certificate_qr(certificate_number: str):

    public_base_url = os.getenv(
        "PUBLIC_BASE_URL",
        "http://127.0.0.1:8000"
    )

    verification_url = (
        f"{public_base_url}/certificates/{certificate_number}"
    )

    qr = qrcode.make(verification_url)

    file_path = f"certificate_{certificate_number}.png"

    qr.save(file_path)

    return FileResponse(
        file_path,
        media_type="image/png",
        filename=file_path
    )
@app.get("/users/{user_id}/dashboard")
def get_dashboard(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own dashboard"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    modules = db.query(TrainingModule).all()

    total_modules = len(modules)
    completed_modules = 0
    module_data = []

    total_drills = 0
    completed_drills = 0

    for module in modules:

        # LESSON PROGRESS
        lessons = db.query(Lesson).filter(
            Lesson.module_id == module.id
        ).all()

        total_lessons = len(lessons)
        completed_lessons = 0

        if lessons:
            lesson_ids = [
                lesson.id
                for lesson in lessons
            ]

            completed_lessons = db.query(
                LessonProgress
            ).filter(
                LessonProgress.user_id == user_id,
                LessonProgress.completed == True,
                LessonProgress.lesson_id.in_(lesson_ids)
            ).count()

        lesson_progress = (
            (completed_lessons / total_lessons) * 100
            if total_lessons > 0
            else 0
        )

        # DRILL PROGRESS
        drills = db.query(TrainingDrill).filter(
            TrainingDrill.module_id == module.id
        ).all()

        module_total_drills = len(drills)
        module_completed_drills = 0

        if drills:
            drill_ids = [
                drill.id
                for drill in drills
            ]

            module_completed_drills = db.query(
                DrillProgress
            ).filter(
                DrillProgress.user_id == user_id,
                DrillProgress.completed == True,
                DrillProgress.drill_id.in_(drill_ids)
            ).count()

        drill_progress = (
            (module_completed_drills / module_total_drills) * 100
            if module_total_drills > 0
            else 0
        )

        total_drills += module_total_drills
        completed_drills += module_completed_drills

        # DRILL QUIZ
        latest_drill_quiz = None

        if drills:
            drill_ids = [
                drill.id
                for drill in drills
            ]

            latest_drill_quiz = db.query(
                DrillQuizAttempt
            ).filter(
                DrillQuizAttempt.user_id == user_id,
                DrillQuizAttempt.drill_id.in_(drill_ids)
            ).order_by(
                DrillQuizAttempt.id.desc()
            ).first()

        drill_quiz_percentage = (
            latest_drill_quiz.percentage
            if latest_drill_quiz
            else None
        )

        # REGULAR MODULE QUIZ
        latest_quiz = db.query(
            QuizAttempt
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.module_id == module.id
        ).order_by(
            QuizAttempt.id.desc()
        ).first()

        quiz_percentage = (
            latest_quiz.percentage
            if latest_quiz
            else None
        )

        # MODULE COMPLETION

        lessons_complete = (
            total_lessons == completed_lessons
            if total_lessons > 0
            else True
        )

        drills_complete = (
            module_total_drills == module_completed_drills
            if module_total_drills > 0
            else True
        )

        quiz_complete = (
            quiz_percentage is not None
            and quiz_percentage >= 70
        )

        # Check every drill quiz
        drill_quizzes_complete = True

        if drills:
            for drill in drills:

                latest_drill_quiz_for_drill = db.query(
                    DrillQuizAttempt
                ).filter(
                    DrillQuizAttempt.user_id == user_id,
                    DrillQuizAttempt.drill_id == drill.id
                ).order_by(
                    DrillQuizAttempt.id.desc()
                ).first()

                if (
                    not latest_drill_quiz_for_drill
                    or latest_drill_quiz_for_drill.percentage < 70
                ):
                    drill_quizzes_complete = False
                    break

        # Final module completion rule
        module_completed = (
            lessons_complete
            and drills_complete
            and quiz_complete
            and drill_quizzes_complete
        )

        if module_completed:
            completed_modules += 1

        # CERTIFICATE
        certificate = db.query(
            Certificate
        ).filter(
            Certificate.user_id == user_id,
            Certificate.module_id == module.id
        ).first()

        # MODULE OVERALL PROGRESS
        progress_parts = []

        if total_lessons > 0:
            progress_parts.append(lesson_progress)

        if module_total_drills > 0:
            progress_parts.append(drill_progress)

        if quiz_percentage is not None:
            progress_parts.append(quiz_percentage)

        if drill_quiz_percentage is not None:
            progress_parts.append(drill_quiz_percentage)

        module_progress = (
            sum(progress_parts) / len(progress_parts)
            if progress_parts
            else 0
        )

        # MODULE DATA
        module_data.append({
            "module_id": module.id,
            "title": module.title,
            "difficulty": module.difficulty,
            "language": module.language,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "lesson_progress": round(
                lesson_progress,
                2
            ),
            "total_drills": module_total_drills,
            "completed_drills": module_completed_drills,
            "drill_progress": round(
                drill_progress,
                2
            ),
            "quiz_percentage": quiz_percentage,
            "latest_drill_quiz_percentage": (
                drill_quiz_percentage
            ),
            "drill_quiz_passed": (
                latest_drill_quiz.passed
                if latest_drill_quiz
                else None
            ),
            "progress": round(
                module_progress,
                2
            ),
            "completed": module_completed,
            "certificate_number": (
                certificate.certificate_number
                if certificate
                else None
            )
        })

    # OVERALL PROGRESS
    module_progress_values = [
        module["progress"]
        for module in module_data
    ]

    overall_progress = (
        sum(module_progress_values)
        / len(module_progress_values)
        if module_progress_values
        else 0
    )

    # FINAL DASHBOARD RESPONSE
    return {
        "user_id": user.id,
        "user_name": user.name,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "total_drills": total_drills,
        "completed_drills": completed_drills,
        "overall_progress": round(
            overall_progress,
            2
        ),
        "modules": module_data
    }

@app.get("/lessons/{lesson_id}/translations")
def get_lesson_translations(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        return {"message": "Lesson not found"}

    translations = db.query(LessonTranslation).filter(
        LessonTranslation.lesson_id == lesson_id
    ).all()

    return translations
@app.get("/lessons/{lesson_id}/language/{language}")
def get_lesson_by_language(
    lesson_id: int,
    language: str,
    db: Session = Depends(get_db)
):
    translation = db.query(LessonTranslation).filter(
        LessonTranslation.lesson_id == lesson_id,
        LessonTranslation.language == language
    ).first()

    if not translation:
        return {
            "message": "Translation not found",
            "language": language
        }

    return translation

@app.put("/modules/{module_id}")
def update_module(
    module_id: int,
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    module.title = module_data.title
    module.description = module_data.description
    module.difficulty = module_data.difficulty
    module.language = module_data.language

    db.commit()
    db.refresh(module)

    return module

@app.delete("/modules/{module_id}")
def delete_module(
    module_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        return {"message": "Module not found"}

    db.delete(module)
    db.commit()

    return {
        "message": "Module deleted successfully"
    }

@app.put("/lessons/{lesson_id}")
def update_lesson(
    lesson_id: int,
    lesson_data: LessonCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        return {"message": "Lesson not found"}

    lesson.title = lesson_data.title
    lesson.content = lesson_data.content

    db.commit()
    db.refresh(lesson)

    return lesson

@app.delete("/lessons/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    

    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        return {"message": "Lesson not found"}

    db.delete(lesson)
    db.commit()

    return {
        "message": "Lesson deleted successfully"
    }

@app.put("/questions/{question_id}")
def update_question(
    question_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id
    ).first()

    if not question:
        return {"message": "Question not found"}

    question.question = question_data.question
    question.option_a = question_data.option_a
    question.option_b = question_data.option_b
    question.option_c = question_data.option_c
    question.option_d = question_data.option_d
    question.correct_answer = question_data.correct_answer

    db.commit()
    db.refresh(question)

    return question

@app.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id
    ).first()

    if not question:
        return {"message": "Question not found"}

    db.delete(question)
    db.commit()

    return {
        "message": "Question deleted successfully"
    }

def admin_required(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

@app.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = password_hash.verify(
        login_data.password,
        user.password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }

@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }

@app.post("/modules/{module_id}/drills")
def create_drill(
    module_id: int,
    drill_data: TrainingDrillCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    drill = TrainingDrill(
    module_id=module_id,
    title=drill_data.title,
    description=drill_data.description,
    instructions=drill_data.instructions,
    difficulty=drill_data.difficulty,
    ar_scene=drill_data.ar_scene,
    equipment=drill_data.equipment,
    scenario=drill_data.scenario,
    hazard_type=drill_data.hazard_type,
    safety_action=drill_data.safety_action
)

    db.add(drill)
    db.commit()
    db.refresh(drill)

    return drill



@app.get("/drills/{drill_id}")
def get_drill(
    drill_id: int,
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    return drill

@app.put("/drills/{drill_id}")
def update_drill(
    drill_id: int,
    drill_data: TrainingDrillCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    drill.title = drill_data.title
    drill.description = drill_data.description
    drill.instructions = drill_data.instructions
    drill.difficulty = drill_data.difficulty

    drill.ar_scene = drill_data.ar_scene
    drill.equipment = drill_data.equipment
    drill.scenario = drill_data.scenario
    drill.hazard_type = drill_data.hazard_type
    drill.safety_action = drill_data.safety_action

    db.commit()
    db.refresh(drill)

    return drill

@app.delete("/drills/{drill_id}")
def delete_drill(
    drill_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    db.delete(drill)
    db.commit()

    return {
        "message": "Drill deleted successfully"
    }

@app.post("/users/{user_id}/drills/{drill_id}/progress")
def update_drill_progress(
    user_id: int,
    drill_id: int,
    progress_data: DrillProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own drill progress"
        )

    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    progress = db.query(DrillProgress).filter(
        DrillProgress.user_id == user_id,
        DrillProgress.drill_id == drill_id
    ).first()

    if progress:
        progress.completed = progress_data.completed
    else:
        progress = DrillProgress(
            user_id=user_id,
            drill_id=drill_id,
            completed=progress_data.completed
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)

    return progress

@app.get("/users/{user_id}/drill-progress")
def get_drill_progress(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own drill progress"
        )

    progress = db.query(DrillProgress).filter(
        DrillProgress.user_id == user_id
    ).all()

    return progress

@app.post("/drills/{drill_id}/questions")
def create_drill_question(
    drill_id: int,
    question_data: DrillQuestionCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    question = DrillQuestion(
        drill_id=drill_id,
        question=question_data.question,
        option_a=question_data.option_a,
        option_b=question_data.option_b,
        option_c=question_data.option_c,
        option_d=question_data.option_d,
        correct_answer=question_data.correct_answer
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question

@app.get("/drills/{drill_id}/questions")
def get_drill_questions(
    drill_id: int,
    language: str = "en",
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    questions = db.query(DrillQuestion).filter(
        DrillQuestion.drill_id == drill_id
    ).all()

    result = []

    for question in questions:

        # English = original question
        if language == "en":
            result.append({
                "id": question.id,
                "question": question.question,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d
            })

        else:
            translation = db.query(DrillQuestionTranslation).filter(
                DrillQuestionTranslation.question_id == question.id,
                DrillQuestionTranslation.language == language
            ).first()

            # If translation exists, return it
            if translation:
                result.append({
                    "id": question.id,
                    "question": translation.question,
                    "option_a": translation.option_a,
                    "option_b": translation.option_b,
                    "option_c": translation.option_c,
                    "option_d": translation.option_d
                })

            # If translation doesn't exist, fall back to English
            else:
                result.append({
                    "id": question.id,
                    "question": question.question,
                    "option_a": question.option_a,
                    "option_b": question.option_b,
                    "option_c": question.option_c,
                    "option_d": question.option_d
                })

    return result

@app.put("/drill-questions/{question_id}")
def update_drill_question(
    question_id: int,
    question_data: DrillQuestionCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(DrillQuestion).filter(
        DrillQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    question.question = question_data.question
    question.option_a = question_data.option_a
    question.option_b = question_data.option_b
    question.option_c = question_data.option_c
    question.option_d = question_data.option_d
    question.correct_answer = question_data.correct_answer

    db.commit()
    db.refresh(question)

    return question

@app.delete("/drill-questions/{question_id}")
def delete_drill_question(
    question_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(DrillQuestion).filter(
        DrillQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    db.delete(question)
    db.commit()

    return {
        "message": "Drill question deleted successfully"
    }

@app.post("/users/{user_id}/drills/{drill_id}/quiz")
def submit_drill_quiz(
    user_id: int,
    drill_id: int,
    submission: DrillQuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit a quiz for yourself"
        )

    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    questions = db.query(DrillQuestion).filter(
        DrillQuestion.drill_id == drill_id
    ).all()

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="No questions found for this drill"
        )

    score = 0

    for question in questions:
        answer = submission.answers.get(question.id)

        if answer and answer.upper() == question.correct_answer.upper():
            score += 1

    total_questions = len(questions)

    percentage = (score / total_questions) * 100

    passed = percentage >= 70

    attempt = DrillQuizAttempt(
        user_id=current_user.id,
        drill_id=drill_id,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        passed=passed
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "user_id": current_user.id,
        "drill_id": drill_id,
        "score": score,
        "total_questions": total_questions,
        "percentage": round(percentage, 2),
        "passed": passed
    }

@app.get("/users/{user_id}/drill-quiz-attempts")
def get_drill_quiz_attempts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own drill quiz history"
        )

    attempts = db.query(DrillQuizAttempt).filter(
        DrillQuizAttempt.user_id == user_id
    ).order_by(
        DrillQuizAttempt.id.desc()
    ).all()

    return attempts

@app.get("/lessons/{lesson_id}/content")
def get_lesson_content(
    lesson_id: int,
    language: str = "English",
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    translation = db.query(LessonTranslation).filter(
        LessonTranslation.lesson_id == lesson_id,
        LessonTranslation.language.ilike(language)
    ).first()

    if translation:
        return {
            "lesson_id": lesson.id,
            "language": translation.language,
            "title": translation.title,
            "content": translation.content,
            "translated": True
        }

    return {
        "lesson_id": lesson.id,
        "language": "English",
        "title": lesson.title,
        "content": lesson.content,
        "translated": False,
        "message": f"No {language} translation found. Showing original lesson."
    }

@app.post("/questions/{question_id}/translations")
def create_question_translation(
    question_id: int,
    translation_data: QuestionTranslationCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    translation = QuestionTranslation(
        question_id=question_id,
        language=translation_data.language,
        question=translation_data.question,
        option_a=translation_data.option_a,
        option_b=translation_data.option_b,
        option_c=translation_data.option_c,
        option_d=translation_data.option_d
    )

    db.add(translation)
    db.commit()
    db.refresh(translation)

    return translation

@app.get("/questions/{question_id}/language/{language}")
def get_question_in_language(
    question_id: int,
    language: str,
    db: Session = Depends(get_db)
):
    question = db.query(QuizQuestion).filter(
        QuizQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    translation = db.query(QuestionTranslation).filter(
        QuestionTranslation.question_id == question_id,
        QuestionTranslation.language.ilike(language)
    ).first()

    if translation:
        return {
            "id": question.id,
            "language": translation.language,
            "question": translation.question,
            "option_a": translation.option_a,
            "option_b": translation.option_b,
            "option_c": translation.option_c,
            "option_d": translation.option_d,
            "translated": True
        }

    return {
        "id": question.id,
        "language": "English",
        "question": question.question,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "translated": False,
        "message": f"No {language} translation found. Showing original question."
    }

@app.post("/drill-questions/{question_id}/translations")
def create_drill_question_translation(
    question_id: int,
    translation_data: DrillQuestionTranslationCreate,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    question = db.query(DrillQuestion).filter(
        DrillQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Drill question not found"
        )

    translation = DrillQuestionTranslation(
        question_id=question_id,
        language=translation_data.language,
        question=translation_data.question,
        option_a=translation_data.option_a,
        option_b=translation_data.option_b,
        option_c=translation_data.option_c,
        option_d=translation_data.option_d
    )

    db.add(translation)
    db.commit()
    db.refresh(translation)

    return translation

@app.get("/drill-questions/{question_id}/language/{language}")
def get_drill_question_in_language(
    question_id: int,
    language: str,
    db: Session = Depends(get_db)
):
    question = db.query(DrillQuestion).filter(
        DrillQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Drill question not found"
        )

    translation = db.query(DrillQuestionTranslation).filter(
        DrillQuestionTranslation.question_id == question_id,
        DrillQuestionTranslation.language.ilike(language)
    ).first()

    if translation:
        return {
            "id": question.id,
            "language": translation.language,
            "question": translation.question,
            "option_a": translation.option_a,
            "option_b": translation.option_b,
            "option_c": translation.option_c,
            "option_d": translation.option_d,
            "translated": True
        }

    return {
        "id": question.id,
        "language": "English",
        "question": question.question,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "translated": False,
        "message": f"No {language} translation found. Showing original drill question."
    }
@app.get("/modules/{module_id}/drills")
def get_module_drills(
    module_id: int,
    db: Session = Depends(get_db)
):
    module = db.query(TrainingModule).filter(
        TrainingModule.id == module_id
    ).first()

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    drills = db.query(TrainingDrill).filter(
        TrainingDrill.module_id == module_id
    ).all()

    return {
        "module_id": module_id,
        "module_title": module.title,
        "total_drills": len(drills),
        "drills": [
            {
                "id": drill.id,
                "title": drill.title,
                "description": drill.description,
                "instructions": drill.instructions,
                "difficulty": drill.difficulty,
                "ar_scene": drill.ar_scene,
                "equipment": drill.equipment,
                "scenario": drill.scenario,
                "hazard_type": drill.hazard_type,
                "safety_action": drill.safety_action
            }
            for drill in drills
        ]
    }

@app.get("/drills/{drill_id}/details")
def get_drill_details(
    drill_id: int,
    db: Session = Depends(get_db)
):
    drill = db.query(TrainingDrill).filter(
        TrainingDrill.id == drill_id
    ).first()

    if not drill:
        raise HTTPException(
            status_code=404,
            detail="Drill not found"
        )

    questions = db.query(DrillQuestion).filter(
        DrillQuestion.drill_id == drill_id
    ).all()

    return {
        "drill": {
            "id": drill.id,
            "module_id": drill.module_id,
            "title": drill.title,
            "description": drill.description,
            "instructions": drill.instructions,
            "difficulty": drill.difficulty,
            "ar_scene": drill.ar_scene,
            "equipment": drill.equipment,
            "scenario": drill.scenario,
            "hazard_type": drill.hazard_type,
            "safety_action": drill.safety_action
        },
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d
            }
            for question in questions
        ]
    }