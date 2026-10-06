import os
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import pandas as pd

app = Flask(__name__)

# پایگاه داده جامع‌تر شامل برندهای مختلف خودرو و قطعات آن‌ها
BRANDS_DATABASE = {
    "renault": {
        "name": "رنو (RENAULT)",
        "logo": "💎",
        "description": "قطعات هیدرولیک و سیستم تعلیق رنو",
        "parts": [
            {"id": 1, "name": "RENAULT MASTER II", "code": "5007", "type": "Hydraulic", "length": "884mm", "diameter": "27.7mm", "piston": "47.1mm", "thread": "M14X1.5-6H"},
            {"id": 2, "name": "RENAULT MEGANE 1 (SMI)", "code": "5008", "type": "Hydraulic", "length": "632mm", "diameter": "24mm", "piston": "36.3mm", "thread": "M12X1-6H"},
            {"id": 3, "name": "RENAULT CLIO 1", "code": "5009", "type": "Hydraulic", "length": "574.5mm", "diameter": "24mm", "piston": "36.3mm", "thread": "M12X1-6H"},
            {"id": 4, "name": "RENAULT KANGOO", "code": "5009", "type": "Hydraulic", "length": "574.5mm", "diameter": "24mm", "piston": "36.3mm", "thread": "M12X1-6H"},
            {"id": 5, "name": "RENAULT 19", "code": "5010", "type": "Hydraulic", "length": "684mm", "diameter": "25mm", "piston": "36.3mm", "thread": "M12X1-6H"},
            {"id": 6, "name": "RENAULT CLIO 2", "code": "5011", "type": "Hydraulic", "length": "577.5mm", "diameter": "23mm", "piston": "37.3mm", "thread": "M14X1.5-6H"},
            {"id": 7, "name": "RENAULT SANDERO", "code": "5012", "type": "Hydraulic", "length": "623.5mm", "diameter": "24mm", "piston": "36.5mm", "thread": "M12X1-6H"},
            {"id": 8, "name": "RENAULT SYMBOL", "code": "5013", "type": "Hydraulic", "length": "624.5mm", "diameter": "24mm", "piston": "38.7mm", "thread": "M14X1.5-6H"},
            {"id": 9, "name": "RENAULT MASTER 3", "code": "5061", "type": "Hydraulic", "length": "763mm", "diameter": "27.7mm", "piston": "49.17mm", "thread": "M16X1.5-6H"},
            {"id": 10, "name": "RENAULT MEGANE 1", "code": "5062", "type": "Hydraulic", "length": "643mm", "diameter": "23mm", "piston": "37.4mm", "thread": "M14X1.5-6H"},
            {"id": 11, "name": "RENAULT TRAFIC", "code": "5076", "type": "Hydraulic", "length": "629mm", "diameter": "27.7mm", "piston": "45.4mm", "thread": "M12X1-6H"},
            {"id": 12, "name": "RENAULT LAGUNA", "code": "5077", "type": "Hydraulic", "length": "624.7mm", "diameter": "27.7mm", "piston": "42mm", "thread": "M12X1-6H"},
        ]
    },
    "volkswagen": {
        "name": "فولکس‌واگن (VOLKSWAGEN)",
        "logo": "🚗",
        "description": "قطعات استاندارد و تخصصی فولکس‌واگن",
        "parts": [
            {"id": 101, "name": "VW GOLF V", "code": "6001", "type": "Hydraulic", "length": "610mm", "diameter": "25mm", "piston": "38mm", "thread": "M14X1.5-6H"},
            {"id": 102, "name": "VW PASSAT", "code": "6002", "type": "Hydraulic", "length": "650mm", "diameter": "26mm", "piston": "40mm", "thread": "M14X1.5-6H"}
        ]
    },
    "ford": {
        "name": "فورد (FORD)",
        "logo": "🚘",
        "description": "قطعات سیستم هیدرولیک و فرمان فورد",
        "parts": [
            {"id": 201, "name": "FORD FOCUS", "code": "7001", "type": "Hydraulic", "length": "590mm", "diameter": "24mm", "piston": "37mm", "thread": "M12X1-6H"}
        ]
    },
    "fiat": {
        "name": "فیات (FIAT)",
        "logo": "🏁",
        "description": "قطعات اصلی خودروهای فیات",
        "parts": [
            {"id": 301, "name": "FIAT PUNTO", "code": "8001", "type": "Hydraulic", "length": "560mm", "diameter": "22mm", "piston": "35mm", "thread": "M12X1-6H"}
        ]
    },
    "toyota": {
        "name": "تویوتا (TOYOTA)",
        "logo": "🌐",
        "description": "قطعات باکیفیت و باامکانام تویوتا",
        "parts": [
            {"id": 401, "name": "TOYOTA COROLLA", "code": "9001", "type": "Hydraulic", "length": "640mm", "diameter": "25mm", "piston": "38mm", "thread": "M14X1.5-6H"}
        ]
    },
    "opel": {
        "name": "اوپل (OPEL)",
        "logo": "⚡",
        "description": "قطعات تخصصی اوپل",
        "parts": [
            {"id": 501, "name": "OPEL ASTRA", "code": "1001", "type": "Hydraulic", "length": "600mm", "diameter": "24mm", "piston": "36mm", "thread": "M12X1-6H"}
        ]
    },
    "hyundai": {
        "name": "هیوندای (HYUNDAI)",
        "logo": "🔷",
        "description": "قطعات هیدرولیک و تعلیق هیوندای",
        "parts": [
            {"id": 601, "name": "HYUNDAI ACCENT", "code": "1101", "type": "Hydraulic", "length": "615mm", "diameter": "24mm", "piston": "37mm", "thread": "M12X1-6H"}
        ]
    },
    "dacia": {
        "name": "دااسیا (DACIA)",
        "logo": "◼️",
        "description": "قطعات خودروهای داچیا",
        "parts": [
            {"id": 701, "name": "DACIA DUSTER", "code": "1201", "type": "Hydraulic", "length": "630mm", "diameter": "25mm", "piston": "38mm", "thread": "M14X1.5-6H"}
        ]
    },
    "citroen": {
        "name": "سیتروئن (CITROEN)",
        "logo": "🔺",
        "description": "قطعات اصلی سیتروئن",
        "parts": [
            {"id": 801, "name": "CITROEN C4", "code": "1301", "type": "Hydraulic", "length": "620mm", "diameter": "24mm", "piston": "36mm", "thread": "M12X1-6H"}
        ]
    },
    "peugeot": {
        "name": "پژو (PEUGEOT)",
        "logo": "🦁",
        "description": "قطعات تخصصی انواع مدل‌های پژو",
        "parts": [
            {"id": 901, "name": "PEUGEOT 206", "code": "1401", "type": "Hydraulic", "length": "580mm", "diameter": "24mm", "piston": "36mm", "thread": "M12X1-6H"},
            {"id": 902, "name": "PEUGEOT 405", "code": "1402", "type": "Hydraulic", "length": "620mm", "diameter": "25mm", "piston": "38mm", "thread": "M14X1.5-6H"}
        ]
    },
    "audi": {
        "name": "آودی (AUDI)",
        "logo": "⭕",
        "description": "قطعات لوکس و استاندارد آودی",
        "parts": [
            {"id": 1001, "name": "AUDI A4", "code": "1501", "type": "Hydraulic", "length": "660mm", "diameter": "26mm", "piston": "40mm", "thread": "M14X1.5-6H"}
        ]
    },
    "mitsubishi": {
        "name": "میتسوبیشی (MITSUBISHI)",
        "logo": "🔺",
        "description": "قطعات هیدرولیک میتسوبیشی",
        "parts": [
            {"id": 1101, "name": "MITSUBISHI LANCER", "code": "1601", "type": "Hydraulic", "length": "610mm", "diameter": "24mm", "piston": "37mm", "thread": "M12X1-6H"}
        ]
    }
}

# قالب صفحه اصلی (انتخاب برندها مطابق تصویر شما)
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>انتخاب برند خودرو - کاتالوگ دیجیتال قطعات</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Vazirmatn', sans-serif; }</style>
</head>
<body class="bg-slate-100 text-slate-800">
    <div class="container mx-auto px-4 py-12 max-w-6xl">
        <header class="text-center mb-12">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-2">کاتالوگ جامع قطعات هیدرولیک خودرو</h1>
            <p class="text-slate-500">لطفاً برند خودروی مورد نظر خود را برای مشاهده محصولات و کاتالوگ انتخاب کنید</p>
        </header>

        <!-- گرید برندهای خودرو (طراحی مدرن الهام گرفته از تصویر شما) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {% for key, brand in brands.items() %}
            <a href="/brand/{{ key }}" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md hover:border-blue-500 transition group flex flex-col items-center text-center">
                <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition">
                    {{ brand.logo }}
                </div>
                <h2 class="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition mb-1">{{ brand.name }}</h2>
                <p class="text-xs text-slate-400">{{ brand.parts | length }} محصول موجود</p>
            </a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# قالب صفحه کاتالوگ قطعات هر برند (به همراه چت‌بات و سبد سفارش)
CATALOG_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کاتالوگ قطعات {{ brand.name }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Vazirmatn', sans-serif; }</style>
</head>
<body class="bg-gray-100 text-gray-800">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- هدر سایت -->
        <header class="bg-slate-900 text-white p-6 rounded-2xl shadow-lg mb-8 flex flex-col md:flex-row justify-between items-center">
            <div>
                <div class="flex items-center gap-3">
                    <a href="/" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl text-xs transition">← بازگشت به انتخاب برند</a>
                    <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-lg">{{ brand.name }}</span>
                </div>
                <h1 class="text-2xl font-bold mt-2">کاتالوگ تخصصی قطعات هیدرولیک</h1>
                <p class="text-gray-400 text-sm mt-1">{{ brand.description }}</p>
            </div>
            <div class="mt-4 md:mt-0 bg-slate-800 px-4 py-2 rounded-xl text-sm border border-slate-700">
                وضعیت سیستم: <span class="text-green-400 font-semibold">● آنلاین و فعال</span>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- بخش محصولات (کاتالوگ) -->
            <div class="lg:col-span-2 space-y-4">
                <div class="bg-white p-4 rounded-2xl shadow-sm flex items-center justify-between">
                    <input type="text" id="searchInput" placeholder="جستجو بر اساس نام قطعه یا کد فنی..." 
                           class="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                </div>

                <div id="partsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for part in brand.parts %}
                    <div class="part-card bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition"
                         data-name="{{ part.name | lower }}" data-code="{{ part.code }}">
                        <div class="flex justify-between items-start mb-3">
                            <span class="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-lg">{{ part.type }}</span>
                            <span class="text-gray-500 font-mono text-sm">کد: <b>{{ part.code }}</b></span>
                        </div>
                        <h3 class="font-bold text-lg text-slate-800 mb-3">{{ part.name }}</h3>
                        <div class="grid grid-cols-2 gap-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-xl">
                            <div>طول: <b>{{ part.length }}</b></div>
                            <div>قطر شفت: <b>{{ part.diameter }}</b></div>
                            <div>قطر پیستون: <b>{{ part.piston }}</b></div>
                            <div>رزوه: <b>{{ part.thread }}</b></div>
                        </div>
                        <button onclick="addToOrder('{{ part.name }}', '{{ part.code }}')" 
                                class="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-xl text-sm font-medium transition">
                            افزودن به لیست سفارش
                        </button>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- بخش هوش مصنوعی (چت‌بات مشاور) و سبد سفارش -->
            <div class="space-y-6">
                <!-- چت‌بات هوشمند -->
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col h-[400px]">
                    <div class="bg-slate-800 text-white p-4 rounded-t-2xl font-bold text-sm flex items-center gap-2">
                        <span>🤖 مشاور هوشمند قطعات {{ brand.name }}</span>
                    </div>
                    <div id="chatMessages" class="flex-1 p-4 overflow-y-auto space-y-3 text-sm bg-slate-50">
                        <div class="bg-white p-3 rounded-xl shadow-xs border border-gray-200 text-slate-700">
                            سلام! درباره قطعات {{ brand.name }} چه سوالی دارید؟ نام قطعه یا کد فنی را بپرسید.
                        </div>
                    </div>
                    <div class="p-3 bg-white border-t rounded-b-2xl flex gap-2">
                        <input type="text" id="userInput" placeholder="سوال خود را بپرسید..." 
                               class="flex-1 px-3 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                               onkeypress="if(event.key === 'Enter') sendMessage()">
                        <button onclick="sendMessage()" class="bg-slate-900 text-white px-4 py-2 rounded-xl text-sm hover:bg-slate-800">ارسال</button>
                    </div>
                </div>

                <!-- سبد خرید و پیش‌فاکتور -->
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
                    <h2 class="font-bold text-base mb-3 text-slate-800">📋 اقلام انتخاب شده برای سفارش</h2>
                    <ul id="orderList" class="text-sm text-gray-600 divide-y mb-4 min-h-[60px]">
                        <li class="py-2 text-gray-400 text-center">هنوز قطعه‌ای انتخاب نشده است.</li>
                    </ul>
                    <button onclick="submitOrder()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-sm font-bold transition">
                        تایید و ثبت نهایی سفارش
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('searchInput').addEventListener('input', function(e) {
            let term = e.target.value.toLowerCase();
            document.querySelectorAll('.part-card').forEach(card => {
                let name = card.getAttribute('data-name');
                let code = card.getAttribute('data-code');
                if (name.includes(term) || code.includes(term)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });

        let selectedItems = [];

        function addToOrder(name, code) {
            selectedItems.push({name, code});
            updateOrderUI();
        }

        function updateOrderUI() {
            let list = document.getElementById('orderList');
            if (selectedItems.length === 0) {
                list.innerHTML = '<li class="py-2 text-gray-400 text-center">هنوز قطعه‌ای انتخاب نشده است.</li>';
                return;
            }
            list.innerHTML = '';
            selectedItems.forEach((item, index) => {
                list.innerHTML += `<li class="py-2 flex justify-between items-center"><span>${item.name} (کد: ${item.code})</span> <button onclick="removeItem(${index})" class="text-red-500 text-xs">حذف</button></li>`;
            });
        }

        function removeItem(index) {
            selectedItems.splice(index, 1);
            updateOrderUI();
        }

        function sendMessage() {
            let input = document.getElementById('userInput');
            let message = input.value.trim();
            if (!message) return;

            let chatBox = document.getElementById('chatMessages');
            chatBox.innerHTML += `<div class="bg-blue-50 text-blue-900 p-3 rounded-xl ml-8 text-left">${message}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            fetch('/api/chat/{{ brand_key }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(res => res.json())
            .then(data => {
                chatBox.innerHTML += `<div class="bg-white p-3 rounded-xl mr-8 shadow-xs border border-gray-200 text-slate-700">${data.reply}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        }

        function submitOrder() {
            if (selectedItems.length === 0) {
                alert('لطفاً حداقل یک قطعه را انتخاب کنید.');
                return;
            }
            alert('سفارش شما با موفقیت ثبت شد!');
            selectedItems = [];
            updateOrderUI();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, brands=BRANDS_DATABASE)

@app.route('/brand/<brand_key>')
def brand_catalog(brand_key):
    if brand_key not in BRANDS_DATABASE:
        return redirect(url_for('home'))
    brand = BRANDS_DATABASE[brand_key]
    return render_template_string(CATALOG_TEMPLATE, brand=brand, brand_key=brand_key)

@app.route('/api/chat/<brand_key>', methods=['POST'])
def ai_chat(brand_key):
    if brand_key not in BRANDS_DATABASE:
        return jsonify({'reply': 'برند نامعتبر است.'})
    
    data = request.get_json()
    user_msg = data.get('message', '').lower()
    brand_parts = BRANDS_DATABASE[brand_key]['parts']
    
    matched = []
    for part in brand_parts:
        if any(keyword in user_msg for keyword in part['name'].lower().split()) or part['code'] in user_msg:
            matched.append(part)
            
    if matched:
        reply = "بر اساس کاتالوگ این برند، موارد زیر مطابقت دارند:<br>"
        for m in matched:
            reply += f"🔹 <b>{m['name']}</b> (کد: {m['code']}) - طول: {m['length']}<br>"
    else:
        reply = "قطعه‌ای با این مشخصات در این دسته یافت نشد."
        
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)