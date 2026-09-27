import json
from pathlib import Path

FILE = Path("trainingTranslations.json")

data = json.loads(FILE.read_text(encoding="utf-8"))

hi = data.setdefault("hi", {})

translations = {
    "What should a worker do when a hazard is detected inside a mine tunnel?":
        "जब खदान की सुरंग के अंदर कोई खतरा पाया जाए तो कर्मचारी को क्या करना चाहिए?",

    "Ignore the hazard":
        "खतरे को नज़रअंदाज़ करना",

    "Follow the approved safety procedure":
        "स्वीकृत सुरक्षा प्रक्रिया का पालन करना",

    "Continue working normally":
        "सामान्य रूप से काम जारी रखना",

    "Remove safety equipment":
        "सुरक्षा उपकरण हटाना",

    "What should a worker do first during a mine emergency evacuation?":
        "खदान में आपातकालीन निकासी के दौरान कर्मचारी को सबसे पहले क्या करना चाहिए?",

    "Continue working until someone gives further instructions":
        "जब तक कोई आगे के निर्देश न दे तब तक काम जारी रखना",

    "Identify the nearest safe exit and follow the evacuation procedure":
        "निकटतम सुरक्षित निकास की पहचान करना और निकासी प्रक्रिया का पालन करना",

    "Remove the required safety equipment":
        "आवश्यक सुरक्षा उपकरण हटाना",

    "Stay inside the tunnel and wait":
        "सुरंग के अंदर रहकर इंतज़ार करना",

    "Why is ventilation important in underground workings?":
        "भूमिगत कार्यस्थलों में वेंटिलेशन क्यों महत्वपूर्ण है?",

    "It is only needed for comfort":
        "यह केवल आराम के लिए आवश्यक है",

    "It helps maintain safe atmospheric conditions and control hazards":
        "यह सुरक्षित वायुमंडलीय परिस्थितियाँ बनाए रखने और खतरों को नियंत्रित करने में मदद करता है",

    "It replaces all gas monitoring":
        "यह सभी गैस निगरानी का स्थान लेता है",

    "It is used only after an incident":
        "इसका उपयोग केवल किसी घटना के बाद किया जाता है",

    "What should a worker do after an atmospheric warning or abnormal reading?":
        "वायुमंडलीय चेतावनी या असामान्य रीडिंग मिलने के बाद कर्मचारी को क्या करना चाहिए?",

    "Treat it as unimportant if the tunnel looks normal":
        "यदि सुरंग सामान्य दिखाई दे तो इसे महत्वहीन समझना",

    "Follow the site's approved response procedure":
        "साइट की स्वीकृत प्रतिक्रिया प्रक्रिया का पालन करना",

    "Continue deeper into the affected area":
        "प्रभावित क्षेत्र में और अंदर जाना जारी रखना",

    "Disable the warning system":
        "चेतावनी प्रणाली को बंद करना",

    "Who should perform technical ventilation interventions?":
        "तकनीकी वेंटिलेशन हस्तक्षेप किसे करना चाहिए?",

    "Any worker who is nearby":
        "पास में मौजूद कोई भी कर्मचारी",

    "Only trained and authorized personnel under the applicable procedure":
        "लागू प्रक्रिया के अनुसार केवल प्रशिक्षित और अधिकृत कर्मियों को",

    "Visitors":
        "आगंतुकों को",

    "No one":
        "किसी को नहीं",

    "Why should ventilation controls not be disturbed without authorization?":
        "बिना अनुमति वेंटिलेशन नियंत्रणों में बदलाव क्यों नहीं करना चाहिए?",

    "Ventilation changes can affect underground atmospheric conditions and safety":
        "वेंटिलेशन में बदलाव भूमिगत वायुमंडलीय परिस्थितियों और सुरक्षा को प्रभावित कर सकते हैं",

    "Ventilation has no safety function":
        "वेंटिलेशन का कोई सुरक्षा कार्य नहीं है",

    "It only changes lighting":
        "यह केवल प्रकाश व्यवस्था बदलता है",

    "It affects personal belongings":
        "यह व्यक्तिगत सामान को प्रभावित करता है",

    "Can a hazardous atmosphere always be identified visually?":
        "क्या खतरनाक वायुमंडलीय स्थिति की पहचान हमेशा देखकर की जा सकती है?",

    "Yes, because every hazardous gas is visible":
        "हाँ, क्योंकि हर खतरनाक गैस दिखाई देती है",

    "No, visual appearance alone is not a reliable safety check":
        "नहीं, केवल देखकर स्थिति की जाँच करना विश्वसनीय सुरक्षा उपाय नहीं है",

    "Only during daylight":
        "केवल दिन के समय",

    "Only when machinery is running":
        "केवल तब जब मशीनरी चल रही हो",

    "What should happen when a worker is instructed to leave an unsafe tunnel area?":
        "जब किसी कर्मचारी को असुरक्षित सुरंग क्षेत्र छोड़ने का निर्देश दिया जाए तो क्या करना चाहिए?",

    "Remain there until the warning disappears":
        "चेतावनी समाप्त होने तक वहीं रहना",

    "Follow the approved evacuation or safe-movement procedure":
        "स्वीकृत निकासी या सुरक्षित स्थानांतरण प्रक्रिया का पालन करना",

    "Explore another unsafe area":
        "किसी अन्य असुरक्षित क्षेत्र की जाँच करना",

    "Ignore the instruction":
        "निर्देश को अनदेखा करना",

    "Why is communication important during a tunnel emergency?":
        "सुरंग में आपातकाल के दौरान संचार क्यों महत्वपूर्ण है?",

    "It helps the approved response process receive information about the hazard":
        "यह स्वीकृत प्रतिक्रिया प्रक्रिया तक खतरे की जानकारी पहुँचाने में मदद करता है",

    "It removes the need for evacuation":
        "इससे निकासी की आवश्यकता समाप्त हो जाती है",

    "It guarantees the hazard has ended":
        "यह सुनिश्चित करता है कि खतरा समाप्त हो गया है",

    "It replaces all emergency procedures":
        "यह सभी आपातकालीन प्रक्रियाओं का स्थान लेता है",

    "What is the main learning objective of the tunnel AR drill?":
        "सुरंग AR ड्रिल का मुख्य सीखने का उद्देश्य क्या है?",

    "Practice safe decision-making around a simulated tunnel hazard":
        "सिमुलेट किए गए सुरंग खतरे के आसपास सुरक्षित निर्णय लेने का अभ्यास करना",

    "Practice untrained equipment repair":
        "बिना प्रशिक्षण के उपकरण मरम्मत का अभ्यास करना",

    "Practice entering unsafe areas":
        "असुरक्षित क्षेत्रों में प्रवेश करने का अभ्यास करना",

    "Practice disabling alarms":
        "अलार्म बंद करने का अभ्यास करना",
}

added = 0
updated = 0

for english, hindi in translations.items():
    if english in hi:
        if hi[english] != hindi:
            hi[english] = hindi
            updated += 1
    else:
        hi[english] = hindi
        added += 1

FILE.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Hindi drill translations patched successfully.")
print(f"Added: {added}")
print(f"Updated: {updated}")
print(f"Total translations in Hindi section: {len(hi)}")