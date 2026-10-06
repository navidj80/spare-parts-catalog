import os
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import pandas as pd

app = Flask(__name__)

# پایگاه داده شامل برندها با مسیر دقیق تصاویر پوشه brand و part
BRANDS_DATABASE = {
    "renault": {
        "name": "رنو (RENAULT)",
        "logo": "/static/images/brand/renault.png",
        "description": "قطعات هیدرولیک و سیستم تعلیق رنو",
        "parts": [
            {
                "id": 1, 
                "name": "RENAULT MASTER II", 
                "code": "5007", 
                "type": "Hydraulic", 
                "length": "884mm", 
                "diameter": "27.7mm", 
                "piston": "47.1mm", 
                "thread": "M14X1.5-6H",
                "image": "/static/images/part/part1.png"
            },
            {
                "id": 2, 
                "name": "RENAULT MEGANE 1 (SMI)", 
                "code": "5008", 
                "type": "Hydraulic", 
                "length": "632mm", 
                "diameter": "24mm", 
                "piston": "36.3mm", 
                "thread": "M12X1-6H",
                "image": "" # اگر عکسی برای این قطعه نداشتید خالی بگذارید
            },
        ]
    },

    "VOLKSWAGEN": {
        "name": "فولکس‌واگن (VOLKSWAGEN)",
        "logo": "/static/images/brand/volkswagen.png",
        "description": "قطعات استاندارد و اورجینال فولکس‌واگن",
        "parts": []
    },
    "FORD": {
        "name": "فورد (FORD)",
        "logo": "/static/images/brand/ford.png",
        "description": "قطعات هیدرولیک و موتوری فورد",
        "parts": []
    },
    "FIAT": {
        "name": "فیات (FIAT)",
        "logo": "/static/images/brand/fiat.png",
        "description": "قطعات تخصصی خودروهای فیات",
        "parts": []
    },
    "TOYOTA": {
        "name": "تویوتا (TOYOTA)",
        "logo": "/static/images/brand/toyota.png",
        "description": "قطعات باکیفیت و ژاپنی تویوتا",
        "parts": []
    },
    "OPEL": {
        "name": "اوپل (OPEL)",
        "logo": "/static/images/brand/opel.png",
        "description": "قطعات یدکی و سیستم تعلیق اوپل",
        "parts": []
    },
    "HYUNDAI": {
        "name": "هیوندای (HYUNDAI)",
        "logo": "/static/images/brand/hyundai.png",
        "description": "قطعات شرکتی هیوندای",
        "parts": []
    },
    "DACIA": {
        "name": "داچیا (DACIA)",
        "logo": "/static/images/brand/dacia.png",
        "description": "قطعات تخصصی محصولات داچیا",
        "parts": []
    },
    "CITROEN": {
        "name": "سیتروئن (CITROEN)",
        "logo": "/static/images/brand/citroen.png",
        "description": "قطعات هیدرولیک و جلوبندی سیتروئن",
        "parts": []
    },
    "PEUGEOT": {
        "name": "پژو (PEUGEOT)",
        "logo": "/static/images/brand/peugeot.png",
        "description": "قطعات تخصصی و هیدرولیک پژو",
        "parts": []
    },
    "AUDI": {
        "name": "آودی (AUDI)",
        "logo": "/static/images/brand/audi.png",
        "description": "قطعات لوکس و استاندارد آودی",
        "parts": []
    },
    "MITSUBISHI": {
        "name": "میتسوبیشی (MITSUBISHI)",
        "logo": "/static/images/brand/mitsubishi.png",
        "description": "قطعات ژاپنی و مقاوم میتسوبیشی",
        "parts": []
    },
    "KIA": {
        "name": "کیا (KIA)",
        "logo": "/static/images/brand/kia.png",
        "description": "قطعات اصلی خودروهای کیا",
        "parts": []
    },
    "HONDA": {
        "name": "هوندا (HONDA)",
        "logo": "/static/images/brand/honda.png",
        "description": "قطعات استاندارد هوندا",
        "parts": []
    },
    "BMW": {
        "name": "بی‌ام‌و (BMW)",
        "logo": "/static/images/brand/bmw.png",
        "description": "قطعات تخصصی خودروهای بی‌ام‌و",
        "parts": []
    },
    "SKODA": {
        "name": "اشکودا (SKODA)",
        "logo": "/static/images/brand/skoda.png",
        "description": "قطعات یدکی اشکودا",
        "parts": []
    },
    "SEAT": {
        "name": "سئات (SEAT)",
        "logo": "/static/images/brand/seat.png",
        "description": "قطعات خودروهای سئات",
        "parts": []
    },
    "VOLVO": {
        "name": "ولوو (VOLVO)",
        "logo": "/static/images/brand/volvo.png",
        "description": "قطعات سنگین و سواری ولوو",
        "parts": []
    },
    "CHEVROLET": {
        "name": "شورولت (CHEVROLET)",
        "logo": "/static/images/brand/chevrolet.png",
        "description": "قطعات خودروهای آمریکایی شورولت",
        "parts": []
    },
    "MERCEDES BENZ": {
        "name": "مرسدس بنز (MERCEDES BENZ)",
        "logo": "/static/images/brand/mercedes.png",
        "description": "قطعات تخصصی مرسدس بنز",
        "parts": []
    },
    "IVECO": {
        "name": "ایوکو (IVECO)",
        "logo": "/static/images/brand/iveco.png",
        "description": "قطعات خودروهای تجاری و سنگین ایوکو",
        "parts": []
    },
    "SSANG-YONG": {
        "name": "سانگ‌یانگ (SSANG-YONG)",
        "logo": "/static/images/brand/ssangyong.png",
        "description": "قطعات خودروهای شاسی‌بلند سانگ‌یانگ",
        "parts": []
    },
    "CHERY": {
        "name": "چری (CHERY)",
        "logo": "/static/images/brand/chery.png",
        "description": "قطعات خودروهای چری",
        "parts": []
    },
    "KARSAN": {
        "name": "کارسان (KARSAN)",
        "logo": "/static/images/brand/karsan.png",
        "description": "قطعات خودروهای تجاری کارسان",
        "parts": []
    },
    "TOFAS": {
        "name": "توفاش (TOFAS)",
        "logo": "/static/images/brand/tofas.png",
        "description": "قطعات تخصصی توفاش",
        "parts": []
    }
}

# قالب صفحه اصلی (نمایش لوگوی برندها از پوشه brand)
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>انتخاب برند خودرو - کاتالوگ دیجیتال</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Vazirmatn', sans-serif; }</style>
</head>
<body class="bg-slate-100 text-slate-800">
    <div class="container mx-auto px-4 py-12 max-w-6xl">
        <header class="text-center mb-12">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-2">کاتالوگ جامع قطعات هیدرولیک خودرو</h1>
            <p class="text-slate-500">لطفاً برند خودروی مورد نظر خود را انتخاب کنید</p>
        </header>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {% for key, brand in brands.items() %}
            <a href="/brand/{{ key }}" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md hover:border-blue-500 transition group flex flex-col items-center text-center">
                <div class="w-20 h-20 bg-slate-50 rounded-2xl flex items-center justify-center mb-4 overflow-hidden border border-slate-100 p-2">
                    <img src="{{ brand.logo }}" alt="{{ brand.name }}" class="w-full h-full object-contain group-hover:scale-110 transition">
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

# قالب صفحه کاتالوگ قطعات (نمایش عکس قطعه از پوشه part در صورت وجود)
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
        <header class="bg-slate-900 text-white p-6 rounded-2xl shadow-lg mb-8 flex flex-col md:flex-row justify-between items-center">
            <div>
                <div class="flex items-center gap-3">
                    <a href="/" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-xl text-xs transition">← بازگشت به انتخاب برند</a>
                    <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-lg">{{ brand.name }}</span>
                </div>
                <h1 class="text-2xl font-bold mt-2">کاتالوگ تخصصی قطعات هیدرولیک</h1>
                <p class="text-gray-400 text-sm mt-1">{{ brand.description }}</p>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 space-y-4">
                <div class="bg-white p-4 rounded-2xl shadow-sm flex items-center justify-between">
                    <input type="text" id="searchInput" placeholder="جستجو بر اساس نام قطعه یا کد فنی..." 
                           class="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                </div>

                <div id="partsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for part in brand.parts %}
                    <div class="part-card bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition"
                         data-name="{{ part.name | lower }}" data-code="{{ part.code }}">
                        
                        <!-- نمایش عکس قطعه در صورت وجود -->
                        {% if part.image %}
                        <div class="w-full h-40 bg-slate-50 rounded-xl mb-4 overflow-hidden border border-slate-100 p-2">
                            <img src="{{ part.image }}" alt="{{ part.name }}" class="w-full h-full object-contain">
                        </div>
                        {% endif %}

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

            <!-- پنل چت و سفارش -->
            <div class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col h-[400px]">
                    <div class="bg-slate-800 text-white p-4 rounded-t-2xl font-bold text-sm">
                        <span>🤖 مشاور هوشمند قطعات {{ brand.name }}</span>
                    </div>
                    <div id="chatMessages" class="flex-1 p-4 overflow-y-auto space-y-3 text-sm bg-slate-50">
                        <div class="bg-white p-3 rounded-xl shadow-xs border border-gray-200 text-slate-700">
                            سلام! درباره قطعات {{ brand.name }} چه سوالی دارید؟
                        </div>
                    </div>
                    <div class="p-3 bg-white border-t rounded-b-2xl flex gap-2">
                        <input type="text" id="userInput" placeholder="سوال خود را بپرسید..." 
                               class="flex-1 px-3 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                               onkeypress="if(event.key === 'Enter') sendMessage()">
                        <button onclick="sendMessage()" class="bg-slate-900 text-white px-4 py-2 rounded-xl text-sm">ارسال</button>
                    </div>
                </div>

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