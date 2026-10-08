"""كتالوج الخدمات - مصدر واحد للبيانات (كان معرّف 3 مرات في الكود الأصلي)."""

categories = {
    "Engine": [
        {"id": 1, "name": "Engine Oil Repair", "description": "Fix oil leakage and check filter", "base_price": 400},
        {"id": 2, "name": "Oil Change", "description": "Change oil and filter completely", "base_price": 300},
        {"id": 3, "name": "Air Filter Repair", "description": "Clean or repair air filter", "base_price": 200},
        {"id": 4, "name": "Air Filter Replacement", "description": "Install new air filter", "base_price": 350},
        {"id": 5, "name": "Fuel Filter Repair", "description": "Clean or repair fuel filter", "base_price": 250},
    ],
    "Brakes": [
        {"id": 15, "name": "Brake Repair", "description": "Inspect and repair brake system", "base_price": 500},
        {"id": 16, "name": "Brake Replacement", "description": "Replace front and rear brake pads", "base_price": 800},
        {"id": 17, "name": "Disc Repair", "description": "Resurface or repair brake discs", "base_price": 600},
        {"id": 18, "name": "Disc Replacement", "description": "Install new brake discs", "base_price": 1000},
        {"id": 19, "name": "Brake Master Repair", "description": "Fix leakage or weak master cylinder", "base_price": 700},
        {"id": 20, "name": "Brake Master Replacement", "description": "Install new master cylinder", "base_price": 1200},
        {"id": 21, "name": "Brake Fluid Service", "description": "Clean and replace brake fluid", "base_price": 300},
        {"id": 22, "name": "Brake Fluid Replacement", "description": "Replace brake fluid completely", "base_price": 400},
    ],
    "Electrical": [
        {"id": 23, "name": "Battery Repair", "description": "Check battery and fix minor issues", "base_price": 600},
        {"id": 24, "name": "Battery Replacement", "description": "Install new battery", "base_price": 1200},
        {"id": 25, "name": "Alternator Repair", "description": "Repair charging alternator", "base_price": 700},
        {"id": 26, "name": "Alternator Replacement", "description": "Install new alternator", "base_price": 950},
        {"id": 27, "name": "ABS Sensor Repair", "description": "Clean or repair ABS sensor", "base_price": 500},
        {"id": 28, "name": "ABS Sensor Replacement", "description": "Install new ABS sensor", "base_price": 800},
        {"id": 29, "name": "Light Bulb Repair", "description": "Repair or replace small bulbs", "base_price": 150},
        {"id": 30, "name": "Light Bulb Replacement", "description": "Install new bulbs", "base_price": 250},
        {"id": 31, "name": "Fan Motor Repair", "description": "Repair or clean fan motor", "base_price": 400},
        {"id": 32, "name": "Fan Motor Replacement", "description": "Install new fan motor", "base_price": 700},
        {"id": 33, "name": "Wiring Harness Repair", "description": "Repair or weld wires", "base_price": 500},
        {"id": 34, "name": "Wiring Harness Replacement", "description": "Install new wiring harness", "base_price": 1000},
    ],
    "Suspension": [
        {"id": 35, "name": "Shock Absorber Repair", "description": "Repair front and rear shocks", "base_price": 650},
        {"id": 36, "name": "Shock Absorber Replacement", "description": "Install new shocks", "base_price": 1100},
        {"id": 37, "name": "Control Arm Repair", "description": "Repair or replace bushings", "base_price": 500},
        {"id": 38, "name": "Control Arm Replacement", "description": "Install new control arms", "base_price": 900},
        {"id": 39, "name": "Engine Mount Repair", "description": "Repair or tighten mounts", "base_price": 400},
        {"id": 40, "name": "Engine Mount Replacement", "description": "Install new mounts", "base_price": 700},
        {"id": 41, "name": "Steering Rack Repair", "description": "Fix leakage or weak rack", "base_price": 800},
        {"id": 42, "name": "Steering Rack Replacement", "description": "Install new rack", "base_price": 1500},
        {"id": 43, "name": "Tie Rod Repair", "description": "Repair or replace tie rods", "base_price": 350},
        {"id": 44, "name": "Tie Rod Replacement", "description": "Install new tie rods", "base_price": 600},
        {"id": 45, "name": "Bushing Repair", "description": "Repair or replace bushings", "base_price": 300},
        {"id": 46, "name": "Bushing Replacement", "description": "Install new bushings", "base_price": 500},
    ],
    "Cooling": [
        {"id": 47, "name": "Radiator Repair", "description": "Clean and repair radiator", "base_price": 500},
        {"id": 48, "name": "Radiator Replacement", "description": "Install new radiator", "base_price": 900},
        {"id": 49, "name": "Cooling Fan Repair", "description": "Repair or clean cooling fan", "base_price": 400},
        {"id": 50, "name": "Cooling Fan Replacement", "description": "Install new cooling fan", "base_price": 700},
        {"id": 51, "name": "Thermostat Repair", "description": "Clean or repair thermostat", "base_price": 300},
        {"id": 52, "name": "Thermostat Replacement", "description": "Install new thermostat", "base_price": 500},
        {"id": 53, "name": "Water Pump Repair", "description": "Repair cooling water pump", "base_price": 600},
        {"id": 54, "name": "Water Pump Replacement", "description": "Install new water pump", "base_price": 950},
    ],
    "Tires": [
        {"id": 55, "name": "Tire Repair", "description": "Patch and adjust tire pressure", "base_price": 150},
        {"id": 56, "name": "Tire Replacement", "description": "Replace tires completely", "base_price": 600},
        {"id": 57, "name": "Wheel Alignment", "description": "Adjust wheel alignment", "base_price": 250},
        {"id": 58, "name": "Wheel Balancing", "description": "Balance tires", "base_price": 200},
        {"id": 59, "name": "Rim Repair", "description": "Repair or weld rim", "base_price": 400},
        {"id": 60, "name": "Rim Replacement", "description": "Install new rim", "base_price": 700},
    ],
    "Transmission": [
        {"id": 61, "name": "Transmission Oil Service", "description": "Clean and change oil", "base_price": 400},
        {"id": 62, "name": "Transmission Oil Replacement", "description": "Replace oil completely", "base_price": 600},
        {"id": 63, "name": "Clutch Repair", "description": "Repair or tighten clutch", "base_price": 700},
        {"id": 64, "name": "Clutch Replacement", "description": "Install new clutch", "base_price": 1200},
        {"id": 65, "name": "Disc Repair", "description": "Repair or tighten disc", "base_price": 650},
        {"id": 66, "name": "Disc Replacement", "description": "Install new disc", "base_price": 1100},
        {"id": 67, "name": "Manual Transmission Repair", "description": "Repair manual gearbox issues", "base_price": 1000},
        {"id": 68, "name": "Manual Transmission Replacement", "description": "Install new manual gearbox", "base_price": 2500},
        {"id": 69, "name": "Automatic Transmission Repair", "description": "Repair automatic gearbox issues", "base_price": 1500},
        {"id": 70, "name": "Automatic Transmission Replacement", "description": "Install new automatic gearbox", "base_price": 3500},
    ],
    "Exhaust": [
        {"id": 71, "name": "Exhaust Repair", "description": "Repair or weld exhaust", "base_price": 500},
        {"id": 72, "name": "Exhaust Replacement", "description": "Install new exhaust", "base_price": 1200},
        {"id": 73, "name": "Oxygen Sensor Repair", "description": "Clean or repair oxygen sensor", "base_price": 400},
        {"id": 74, "name": "Oxygen Sensor Replacement", "description": "Install new oxygen sensor", "base_price": 800},
        {"id": 75, "name": "Catalytic Converter Repair", "description": "Repair or clean catalytic converter", "base_price": 350},
        {"id": 76, "name": "Catalytic Converter Replacement", "description": "Install new catalytic converter", "base_price": 700},
    ],
    "Air Conditioning": [
        {"id": 77, "name": "AC Repair", "description": "Clean and repair AC system", "base_price": 600},
        {"id": 78, "name": "AC Replacement", "description": "Install new AC unit", "base_price": 2500},
        {"id": 79, "name": "AC Compressor Repair", "description": "Repair or clean compressor", "base_price": 800},
        {"id": 80, "name": "AC Compressor Replacement", "description": "Install new compressor", "base_price": 1500},
        {"id": 81, "name": "AC Filter Repair", "description": "Clean or repair AC filter", "base_price": 300},
        {"id": 82, "name": "AC Filter Replacement", "description": "Install new AC filter", "base_price": 50},
    ],
    "Sensors": [
        {"id": 83, "name": "Temperature Sensor Repair", "description": "Clean or repair temperature sensor", "base_price": 350},
        {"id": 84, "name": "Temperature Sensor Replacement", "description": "Install new temperature sensor", "base_price": 600},
        {"id": 85, "name": "Oil Pressure Sensor Repair", "description": "Clean or repair oil pressure sensor", "base_price": 400},
        {"id": 86, "name": "Oil Pressure Sensor Replacement", "description": "Install new oil pressure sensor", "base_price": 700},
        {"id": 87, "name": "Brake Sensor Repair", "description": "Clean or repair brake sensor", "base_price": 350},
        {"id": 88, "name": "Brake Sensor Replacement", "description": "Install new brake sensor", "base_price": 600},
        {"id": 89, "name": "Oxygen Sensor Repair", "description": "Clean or repair oxygen sensor", "base_price": 400},
        {"id": 90, "name": "Oxygen Sensor Replacement", "description": "Install new oxygen sensor", "base_price": 800},
    ],
    "Computers": [
        {"id": 91, "name": "ABS Unit Repair", "description": "Repair or reprogram ABS unit", "base_price": 1000},
        {"id": 92, "name": "ABS Unit Replacement", "description": "Install new ABS unit", "base_price": 2000},
        {"id": 93, "name": "Airbag Unit Repair", "description": "Repair or reprogram airbag unit", "base_price": 1200},
        {"id": 94, "name": "Airbag Unit Replacement", "description": "Install new airbag unit", "base_price": 2500},
        {"id": 95, "name": "Car Computer Repair", "description": "Diagnose and repair ECU", "base_price": 1500},
        {"id": 96, "name": "Car Computer Replacement", "description": "Install new ECU", "base_price": 3500},
    ],
    "General Services": [
        {"id": 97, "name": "Car Wash", "description": "Interior and exterior car wash", "base_price": 200},
        {"id": 98, "name": "Car Polishing", "description": "Polish paint and remove scratches", "base_price": 400},
        {"id": 99, "name": "Seat Cleaning", "description": "Clean and sanitize car seats", "base_price": 300},
        {"id": 100, "name": "Paint Scratch Repair", "description": "Repair and repaint scratched areas", "base_price": 500},
    ],
    "Detailing": [
        {"id": 101, "name": "Ceramic Coating", "description": "Protect paint with durable ceramic coating", "base_price": 2500},
        {"id": 102, "name": "Headlight Restoration", "description": "Polish and restore cloudy headlights", "base_price": 400},
        {"id": 103, "name": "Windshield Repair", "description": "Repair chips and cracks in windshield", "base_price": 600},
        {"id": 104, "name": "Windshield Replacement", "description": "Install a new windshield", "base_price": 1800},
        {"id": 105, "name": "Interior Detailing", "description": "Deep clean upholstery, dashboard and carpets", "base_price": 700},
        {"id": 106, "name": "Underbody Coating", "description": "Anti-rust protection under the car", "base_price": 1200},
    ],
    "Roadside Assistance": [
        {"id": 107, "name": "Towing Service", "description": "24/7 tow truck to your location", "base_price": 800},
        {"id": 108, "name": "Battery Jump Start", "description": "Emergency battery boost", "base_price": 150},
        {"id": 109, "name": "Flat Tire Assist", "description": "Change your tire on the spot", "base_price": 200},
        {"id": 110, "name": "Emergency Fuel Delivery", "description": "Deliver fuel to your exact location", "base_price": 350},
        {"id": 111, "name": "Lockout Assistance", "description": "Professional help to unlock your car", "base_price": 400},
        {"id": 112, "name": "Full Car Inspection", "description": "Complete 120-point vehicle inspection", "base_price": 500},
    ],
}

# أسماء التصنيفات بالعربية
_CATEGORY_AR = {
    "Engine": "المحرك",
    "Brakes": "الفرامل",
    "Electrical": "الكهرباء",
    "Suspension": "التعليق",
    "Cooling": "التبريد",
    "Tires": "الإطارات",
    "Transmission": "ناقل الحركة",
    "Exhaust": "العادم",
    "Air Conditioning": "التكييف",
    "Sensors": "الحساسات",
    "Computers": "الكمبيوتر",
    "General Services": "خدمات عامة",
    "Detailing": "التلميع والعناية",
    "Roadside Assistance": "المساعدة على الطريق",
}

# أسماء ووصف الخدمات بالعربية (مفاتيحها: id الخدمة)
_NAME_AR = {
    1: "إصلاح زيت المحرك", 2: "تغيير الزيت", 3: "إصلاح فلتر الهواء",
    4: "استبدال فلتر الهواء", 5: "إصلاح فلتر الوقود",
    15: "إصلاح الفرامل", 16: "استبدال الفرامل", 17: "إصلاح التيل",
    18: "استبدال التيل", 19: "إصلاح طرمبة الفرامل",
    20: "استبدال طرمبة الفرامل", 21: "خدمة زيت الفرامل",
    22: "استبدال زيت الفرامل",
    23: "إصلاح البطارية", 24: "استبدال البطارية",
    25: "إصلاح الدينامو", 26: "استبدال الدينامو",
    27: "إصلاح حساس ABS", 28: "استبدال حساس ABS",
    29: "إصلاح اللمبات", 30: "استبدال اللمبات",
    31: "إصلاح مروحة الموتور", 32: "استبدال مروحة الموتور",
    33: "إصلاح الأسلاك الكهربائية", 34: "استبدال الأسلاك الكهربائية",
    35: "إصلاح المساعدين", 36: "استبدال المساعدين",
    37: "إصلاح الأكصدام السفلي", 38: "استبدال الأكصدام السفلي",
    39: "إصلاح صامولة الموتور", 40: "استبدال صامولة الموتور",
    41: "إصلاح طرمبة الدركسيون", 42: "استبدال طرمبة الدركسيون",
    43: "إصلاح سوسته المقود", 44: "استبدال سوسته المقود",
    45: "إصلاح الجلب", 46: "استبدال الجلب",
    47: "إصلاح الرادياتير", 48: "استبدال الرادياتير",
    49: "إصلاح مروحة التبريد", 50: "استبدال مروحة التبريد",
    51: "إصلاح الترموستات", 52: "استبدال الترموستات",
    53: "إصلاح طرمبة المياه", 54: "استبدال طرمبة المياه",
    55: "إصلاح الإطار", 56: "استبدال الإطار",
    57: "ضبط زوايا العجلات", 58: "ترصيص العجلات",
    59: "إصلاح الجنط", 60: "استبدال الجنط",
    61: "خدمة زيت القير", 62: "استبدال زيت القير",
    63: "إصلاح الكلتش", 64: "استبدال الكلتش",
    65: "إصلاح التيل", 66: "استبدال التيل",
    67: "إصلاح القير اليدوي", 68: "استبدال القير اليدوي",
    69: "إصلاح القير الأوتوماتيك", 70: "استبدال القير الأوتوماتيك",
    71: "إصلاح العادم", 72: "استبدال العادم",
    73: "إصلاح حساس الأكسجين", 74: "استبدال حساس الأكسجين",
    75: "إصلاح الحفاز", 76: "استبدال الحفاز",
    77: "إصلاح التكييف", 78: "استبدال التكييف",
    79: "إصلاح كمبروسر التكييف", 80: "استبدال كمبروسر التكييف",
    81: "إصلاح فلتر التكييف", 82: "استبدال فلتر التكييف",
    83: "إصلاح حساس الحرارة", 84: "استبدال حساس الحرارة",
    85: "إصلاح حساس الزيت", 86: "استبدال حساس الزيت",
    87: "إصلاح حساس الفرامل", 88: "استبدال حساس الفرامل",
    89: "إصلاح حساس الأكسجين", 90: "استبدال حساس الأكسجين",
    91: "إصلاح وحدة ABS", 92: "استبدال وحدة ABS",
    93: "إصلاح وحدة الوسائد الهوائية", 94: "استبدال وحدة الوسائد الهوائية",
    95: "إصلاح كمبيوتر السيارة", 96: "استبدال كمبيوتر السيارة",
    97: "غسيل السيارة", 98: "تلميع السيارة",
    99: "تنظيف المقاعد", 100: "إصلاح خدوش الدهان",
    101: "حماية نانو سيراميك", 102: "تلميع الأضواء",
    103: "إصلاح الزجاج الأمامي", 104: "استبدال الزجاج الأمامي",
    105: "عناية كاملة بالداخلية", 106: "عزل السيارة من الصدأ",
    107: "خدمة السحب", 108: "شحن بطارية طارئ",
    109: "مساعدة إطار مثقوب", 110: "توصيل وقود طارئ",
    111: "مساعدة فتح السيارة", 112: "فحص شامل للسيارة",
}

_DESC_AR = {
    1: "إصلاح تسريب الزيت وفحص الفلتر", 2: "تغيير الزيت والفلتر بالكامل",
    3: "تنظيف أو إصلاح فلتر الهواء", 4: "تركيب فلتر هواء جديد",
    5: "تنظيف أو إصلاح فلتر الوقود",
    15: "فحص وإصلاح نظام الفرامل", 16: "استبدال تيل الفرامل الأمامي والخلفي",
    17: "تصنيع أو إصلاح تيل الفرامل", 18: "تركيب تيل فرامل جديد",
    19: "إصلاح تهريب أو ضعف طرمبة الفرامل", 20: "تركيب طرمبة فرامل جديدة",
    21: "تنظيف واستبدال زيت الفرامل", 22: "استبدال زيت الفرامل بالكامل",
    23: "فحص البطارية وإصلاح المشاكل البسيطة", 24: "تركيب بطارية جديدة",
    25: "إصلاح دينامو الشحن", 26: "تركيب دينامو جديد",
    27: "تنظيف أو إصلاح حساس ABS", 28: "تركيب حساس ABS جديد",
    29: "إصلاح أو استبدال اللمبات الصغيرة", 30: "تركيب لمبات جديدة",
    31: "إصلاح أو تنظيف مروحة الموتور", 32: "تركيب مروحة موتور جديدة",
    33: "إصلاح أو لحام الأسلاك الكهربائية", 34: "تركيب أسلاك كهربائية جديدة",
    35: "إصلاح المساعدين الأمامي والخلفي", 36: "تركيب مساعدين جديدين",
    37: "إصلاح أو استبدال الجلب", 38: "تركيب أكصدام سفلي جديد",
    39: "إصلاح أو شد صمامات الموتور", 40: "تركيب صمامات جديدة",
    41: "إصلاح تهريب أو ضعف طرمبة الدركسيون", 42: "تركيب طرمبة دركسيون جديدة",
    43: "إصلاح أو استبدال سوسته المقود", 44: "تركيب سوسته مقود جديدة",
    45: "إصلاح أو استبدال الجلب", 46: "تركيب جلب جديدة",
    47: "تنظيف وإصلاح الرادياتير", 48: "تركيب رادياتير جديد",
    49: "إصلاح أو تنظيف مروحة التبريد", 50: "تركيب مروحة تبريد جديدة",
    51: "تنظيف أو إصلاح الترموستات", 52: "تركيب ترموستات جديد",
    53: "إصلاح طرمبة المياه", 54: "تركيب طرمبة مياه جديدة",
    55: "ترقيع وضبط ضغط الإطار", 56: "استبدال الإطارات بالكامل",
    57: "ضبط زوايا العجلات", 58: "ترصيص الإطارات",
    59: "إصلاح أو لحام الجنط", 60: "تركيب جنط جديد",
    61: "تنظيف وتغيير زيت القير", 62: "استبدال زيت القير بالكامل",
    63: "إصلاح أو شد الكلتش", 64: "تركيب كلتش جديد",
    65: "إصلاح أو شد التيل", 66: "تركيب تيل جديد",
    67: "إصلاح مشاكل القير اليدوي", 68: "تركيب قير يدوي جديد",
    69: "إصلاح مشاكل القير الأوتوماتيك", 70: "تركيب قير أوتوماتيك جديد",
    71: "إصلاح أو لحام العادم", 72: "تركيب عادم جديد",
    73: "تنظيف أو إصلاح حساس الأكسجين", 74: "تركيب حساس أكسجين جديد",
    75: "إصلاح أو تنظيف الحفاز", 76: "تركيب حفاز جديد",
    77: "تنظيف وإصلاح نظام التكييف", 78: "تركيب وحدة تكييف جديدة",
    79: "إصلاح أو تنظيف الكمبروسر", 80: "تركيب كمبروسر جديد",
    81: "تنظيف أو إصلاح فلتر التكييف", 82: "تركيب فلتر تكييف جديد",
    83: "تنظيف أو إصلاح حساس الحرارة", 84: "تركيب حساس حرارة جديد",
    85: "تنظيف أو إصلاح حساس الزيت", 86: "تركيب حساس زيت جديد",
    87: "تنظيف أو إصلاح حساس الفرامل", 88: "تركيب حساس فرامل جديد",
    89: "تنظيف أو إصلاح حساس الأكسجين", 90: "تركيب حساس أكسجين جديد",
    91: "إصلاح أو برمجة وحدة ABS", 92: "تركيب وحدة ABS جديدة",
    93: "إصلاح أو برمجة وحدة الوسائد", 94: "تركيب وحدة وسائد جديدة",
    95: "فحص وإصلاح كمبيوتر السيارة", 96: "تركيب كمبيوتر جديد",
    97: "غسيل السيارة من الداخل والخارج", 98: "تلميع الدهان وإزالة الخدوش",
    99: "تنظيف وتعقيم مقاعد السيارة", 100: "إصلاح ودهان المناطق المخدوشة",
    101: "حماية الدهان بطبقة سيراميك متينة", 102: "تلميع وإعادة تأهيل الأضواء الضبابية",
    103: "إصلاح شروخ وتلف الزجاج الأمامي", 104: "تركيب زجاج أمامي جديد",
    105: "تنظيف عميق للمقاعد والتابلوه والسجاد", 106: "عزل مضاد للصدأ أسفل السيارة",
    107: "سيارة سحب متاحة 24/7 تصل لموقعك", 108: "إنعاش البطارية في حالات الطوارئ",
    109: "تغيير الإطار في مكانك", 110: "توصيل وقود إلى موقعك بالضبط",
    111: "مساعدة محترفة لفتح سيارتك", 112: "فحص كامل للسيارة في 120 نقطة",
}


def localize_service(service, lang="en"):
    """إرجاع نسخة مترجمة من بيانات الخدمة حسب اللغة."""
    if lang == "ar":
        return {
            **service,
            "name": _NAME_AR.get(service["id"], service["name"]),
            "description": _DESC_AR.get(service["id"], service["description"]),
        }
    return service


def localize_category(name, lang="en"):
    return _CATEGORY_AR.get(name, name) if lang == "ar" else name


def get_category_key(name):
    """يحوّل اسم التصنيف (بأي لغة) إلى المفتاح الإنجليزي الأصلي."""
    if name in categories:
        return name
    for key, ar in _CATEGORY_AR.items():
        if name == ar:
            return key
    return None


def get_services_by_category(cat_key, lang="en"):
    """إرجاع خدمات تصنيف معين مترجمة حسب اللغة."""
    if cat_key in categories:
        return [localize_service(s, lang) for s in categories[cat_key]]
    return []


def localize_categories(categories_data, lang="en"):
    return {localize_category(k, lang): v for k, v in categories_data.items()}

def get_localized_service_by_id(service_id, lang="en"):
    return localize_service(get_service_by_id(service_id), lang)

def get_localized_services(lang="en"):
    return [localize_service(s, lang) for s in get_all_services()]


def get_service_by_id(service_id):
    for services in categories.values():
        for service in services:
            if service["id"] == service_id:
                return service
    return None


def get_category_for_service(service_id):
    for cat, services in categories.items():
        for s in services:
            if s["id"] == service_id:
                return cat
    return None


# شكل بصري لكل تصنيف — زي طلبات: باستيل + إيموجي + صورة حقيقية
CATEGORY_VISUAL = {
    "Engine": {"emoji": "🔧", "bg": "#fff3e0", "border": "#ffcc80", "accent": "#e65100"},
    "Brakes": {"emoji": "🛞", "bg": "#ffebee", "border": "#ef9a9a", "accent": "#c62828"},
    "Electrical": {"emoji": "🔋", "bg": "#e3f2fd", "border": "#90caf9", "accent": "#1565c0"},
    "Suspension": {"emoji": "🔩", "bg": "#f3e5f5", "border": "#ce93d8", "accent": "#6a1b9a"},
    "Cooling": {"emoji": "❄️", "bg": "#e0f7fa", "border": "#80deea", "accent": "#00695c"},
    "Tires": {"emoji": "🚗", "bg": "#fff8e1", "border": "#ffe082", "accent": "#f57f17"},
    "Transmission": {"emoji": "⚙️", "bg": "#efebe9", "border": "#bcaaa4", "accent": "#4e342e"},
    "Exhaust": {"emoji": "💨", "bg": "#f1f8e9", "border": "#aed581", "accent": "#33691e"},
    "Air Conditioning": {"emoji": "🌬️", "bg": "#e0f2f1", "border": "#80cbc4", "accent": "#004d40"},
    "Sensors": {"emoji": "📡", "bg": "#fce4ec", "border": "#f48fb1", "accent": "#ad1457"},
    "Computers": {"emoji": "💻", "bg": "#ede7f6", "border": "#b39ddb", "accent": "#4527a0"},
    "General Services": {"emoji": "✨", "bg": "#e8f5e9", "border": "#a5d6a7", "accent": "#2e7d32"},
    "Detailing": {"emoji": "💎", "bg": "#fff9c4", "border": "#fff59d", "accent": "#f9a825"},
    "Roadside Assistance": {"emoji": "🚨", "bg": "#ffebee", "border": "#ef9a9a", "accent": "#b71c1c"},
}

# صور حقيقية لكل تصنيف — من Unsplash Source (صور حقيقية حسب التصنيف)
CATEGORY_IMAGES = {
    "Engine": "https://source.unsplash.com/600x400/?car-engine,engine",
    "Brakes": "https://source.unsplash.com/600x400/?car-brake,brake-disc",
    "Electrical": "https://source.unsplash.com/600x400/?car-battery,auto-electrical",
    "Suspension": "https://source.unsplash.com/600x400/?car-suspension,shock-absorber",
    "Cooling": "https://source.unsplash.com/600x400/?car-radiator,engine-cooling",
    "Tires": "https://source.unsplash.com/600x400/?car-tire,wheel",
    "Transmission": "https://source.unsplash.com/600x400/?car-transmission,gearbox",
    "Exhaust": "https://source.unsplash.com/600x400/?car-exhaust,muffler",
    "Air Conditioning": "https://source.unsplash.com/600x400/?car-air-conditioning,ac-compressor",
    "Sensors": "https://source.unsplash.com/600x400/?car-sensor,automotive-sensor",
    "Computers": "https://source.unsplash.com/600x400/?car-ecu,car-computer",
    "General Services": "https://source.unsplash.com/600x400/?car-wash,car-service",
    "Detailing": "https://source.unsplash.com/600x400/?car-detailing,car-polish",
    "Roadside Assistance": "https://source.unsplash.com/600x400/?tow-truck,roadside-assistance",
}


def get_image_for_service(service_id):
    cat = get_category_for_service(service_id)
    return CATEGORY_IMAGES.get(cat, CATEGORY_IMAGES["Engine"])


def get_visual_for_service(service_id):
    cat = get_category_for_service(service_id)
    return CATEGORY_VISUAL.get(cat, {"emoji": "🔧", "bg": "#fff3e0", "border": "#ffcc80", "accent": "#e65100"})


def get_zone(governorate=None, city=None, address=None):
    """يحدد المنطقة: high للتجمع/زايد/العالية، normal للشعبية، mid للباقي."""
    text = " ".join([str(x or "") for x in [governorate, city, address]])
    high_kw = ["التجمع", "زايد", "أكتوبر", "اكتوبر", "الرحاب", "مدينتي", "المعادي", "المهندسين", "الزمالك", "مصر الجديدة", "مدينة نصر", "الشروق", "العبور", "التجمع الخامس"]
    popular_kw = ["القليوبية", "المرج", "السلام", "إمبابة", "بولاق", "عين شمس", "المطرية", "الخصوص", "شبرا", "الوراق", "الخانكة"]
    for kw in high_kw:
        if kw in text:
            return "high"
    for kw in popular_kw:
        if kw in text:
            return "normal"
    # محافظات شعبية كاملة تعتبر normal
    if governorate == "القليوبية":
        return "normal"
    return "mid"


def get_car_multiplier(car_make):
    """سعر حسب نوع العربية — الفاخر أغلى"""
    if not car_make: return 1.0
    luxury = {"Mercedes":1.8,"BMW":1.8,"Audi":1.75,"Lexus":1.8}
    premium = {"Peugeot":1.35,"Honda":1.35,"Skoda":1.25,"Volkswagen":1.25,"Mitsubishi":1.2,"Toyota":1.25}
    mid = {"MG":1.15,"Chery":1.1,"Geely":1.1,"Opel":1.15,"Suzuki":1.1,"Renault":1.1}
    economy = {"BYD":0.9,"Lada":0.9,"Daewoo":0.88,"Speranza":0.88,"Proton":0.9}
    if car_make in luxury: return luxury[car_make]
    if car_make in premium: return premium[car_make]
    if car_make in mid: return mid[car_make]
    if car_make in economy: return economy[car_make]
    return 1.0  # افتراضي Hyundai,Kia,Nissan,Chevrolet...

def get_adjusted_price(base_price, governorate=None, city=None, address=None, car_make=None):
    """سعر واقعي 2026 + حسب المنطقة + نوع العربية"""
    zone = get_zone(governorate, city, address)
    zone_mult = {"high": 1.5, "mid": 1.2, "normal": 1.0}[zone]
    car_mult = get_car_multiplier(car_make)
    realistic = 2.2
    price = int(base_price * realistic * zone_mult * car_mult)
    return int(round(price / 25) * 25)

# صور العربيات
CAR_IMAGES = {
    "Hyundai":"https://images.unsplash.com/photo-1503736334956-4c8ff8e9299d?w=500",
    "Kia":"https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500",
    "Toyota":"https://images.unsplash.com/photo-1629897048514-3dd74151e4d7?w=500",
    "Nissan":"https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=500",
    "BMW":"https://images.unsplash.com/photo-1555215695-3004980ad54e?w=500",
    "Mercedes":"https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500",
    "Audi":"https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=500",
    "Chevrolet":"https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=500",
    "MG":"https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500",
    "BYD":"https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=500",
}
def get_car_image(car_make):
    return CAR_IMAGES.get(car_make, "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=500")


def get_all_services():
    return [service for services in categories.values() for service in services]


# Car brands and models - شامل كل موديلات مصر 2026
CAR_MAKES = {
    "Hyundai": ["Elantra", "Elantra AD", "Elantra CN7", "Tucson", "Tucson NX4", "Accent RB", "Accent HCI", "Sonata", "Creta", "Bayon", "i10", "Grand i10", "Verna", "Matrix", "Getz", "Santa Fe", "Kona"],
    "Kia": ["Cerato", "Cerato K3", "Sportage", "Sportage NQ5", "Picanto", "Rio", "Sorento", "Soul", "Seltos", "XCeed", "Carens", "K5", "Optima", "Grand Cerato"],
    "Toyota": ["Corolla", "Corolla Cross", "Yaris", "Yaris Cross", "Camry", "RAV4", "Fortuner", "C-HR", "Land Cruiser", "Prado", "Hilux", "Avanza", "Rush", "Veloz"],
    "Nissan": ["Sunny N16", "Sunny N17", "Sunny N18", "Sentra", "Qashqai", "Tiida", "Juke", "Patrol", "Navara", "X-Trail", "Kicks", "Juke Nismo"],
    "Chevrolet": ["Optra", "New Optra", "Aveo", "Cruze", "Spark", "Captiva", "Lanos", "N300", "Malibu", "Equinox", "Groove", "Traverse"],
    "MG": ["ZS", "ZS EV", "HS", "MG5", "MG6", "RX5", "RX5 Plus", "MG3", "MG4", "MG One", "MG7"],
    "BYD": ["F3", "L3", "S5", "F0", "Qin", "Song", "Dolphin", "E2", "Seal"],
    "Chery": ["Tiggo", "Tiggo 3", "Tiggo 4", "Tiggo 5", "Tiggo 7", "Tiggo 7 Pro", "Tiggo 8", "Tiggo 8 Pro", "Arrizo 3", "Arrizo 5", "Arrizo 6", "Envy", "QQ", "Tiggo 2"],
    "Geely": ["Emgrand", "Emgrand 7", "Emgrand X7", "Coolray", "Azkarra", "Okavango", "Binray", "Tugella", "Emgrand GS"],
    "Renault": ["Logan", "New Logan", "Duster", "Sandero", "Stepway", "Fluence", "Megane", "Megane 4", "Captur", "Kadjar", "Koleos", "Clio", "Kwid", "Talisman"],
    "Peugeot": ["301", "2008", "3008", "5008", "508", "208", "308", "3008 GT", "Traveller", "Rifter", "Partner"],
    "Fiat": ["Tipo", "Tipo Hatchback", "Tipo SW", "500", "500X", "500L", "500e", "Panda", "Punto", "Punto Evo", "Doblo", "Fiorino", "Qubo", "500C"],
    "Opel": ["Astra", "Astra GTC", "Corsa", "Mokka", "Mokka X", "Crossland", "Grandland", "Insignia", "Vectra", "Astra K", "Adam"],
    "Skoda": ["Octavia A4", "Octavia A5", "Octavia A7", "Octavia A8", "Fabia", "Superb", "Superb 2023", "Kodiaq", "Karoq", "Scala", "Rapid", "Kamiq"],
    "Volkswagen": ["Jetta", "Jetta 2023", "Passat", "Passat B8", "Golf 7", "Golf 8", "Tiguan", "Tiguan Allspace", "Polo", "T-Roc", "Arteon", "Caddy", "Virtus"],
    "Suzuki": ["Swift", "Swift Dzire", "Baleno", "Dzire", "Vitara", "Grand Vitara", "Ciaz", "Alto", "Jimny", "Ertiga", "S-Cross", "Fronx", "Celerio", "APV"],
    "Mitsubishi": ["Lancer", "Lancer EX", "Lancer Shark", "Outlander", "Attrage", "Mirage", "Eclipse Cross", "Pajero", "Xpander", "ASX", "L200"],
    "Honda": ["Civic", "City", "Accord", "CR-V", "Jazz", "HR-V", "BR-V", "Crosstour", "Pilot", "WR-V"],
    "Mercedes": ["C180", "C200", "C300", "E200", "E300", "S350", "S450", "GLA 200", "GLC 200", "GLC 300", "GLE", "GLS", "A180", "A200", "CLA 180", "CLA 200", "B200"],
    "BMW": ["116", "118", "316", "318", "320", "330", "520", "530", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z4"],
    "Audi": ["A3", "A3 Sedan", "A4", "A5", "A6", "A7", "Q2", "Q3", "Q5", "Q7", "Q8", "A8"],
    "Daewoo": ["Lanos", "Nubira", "Nubira 2", "Leganza", "Matiz", "Cielo", "Espero"],
    "Lada": ["Granta", "Granta Cross", "Vesta", "Vesta Cross", "Niva", "Niva Travel", "X-Ray"],
    "Proton": ["Saga", "Saga 2023", "Gen-2", "Persona", "Exora", "Waja", "Preve"],
    "Speranza": ["A113", "A516", "A620", "Tiggo", "Envy", "M11", "M12", "S11"],
    "Seat": ["Ibiza", "Leon", "Ateca", "Arona", "Tarraco", "Toledo"],
    "Citroen": ["C3", "C4", "C5 Aircross", "C-Elysee", "Berlingo", "Grand C4"],
    "Jeep": ["Renegade", "Cherokee", "Grand Cherokee", "Compass", "Wrangler"],
    "Other": ["Other model"],
}


def get_car_makes():
    return sorted(CAR_MAKES.keys())
