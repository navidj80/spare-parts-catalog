import os
from flask import Flask, render_template_string, request, jsonify
import pandas as pd

app = Flask(__name__)

# پایگاه داده نمونه از قطعات موجود در کاتالوگ شما (رنو)
PARTS_DATABASE = [
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

# قالب صفحه اصلی با طراحی مدرن (Tailwind CSS) و چت‌بات هوشمند متصل به کاتالوگ
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کاتالوگ دیجیتال و مشاور هوشمند لوازم یدکی</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Vazirmatn', sans-serif; }</style>
</head>
<body class="bg-gray-100 text-gray-800">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- هدر سایت -->
        <header class="bg-slate-900 text-white p-6 rounded-2xl shadow-lg mb-8 flex flex-col md:flex-row justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold">کاتالوگ هوشمند قطعات هیدرولیک خودرو</h1>
                <p class="text-gray-400 text-sm mt-1">جستجوی سریع محصولات و مشاوره هوشمند خرید قطعات رنو</p>
            </div>
            <div class="mt-4 md:mt-0 bg-slate-800 px-4 py-2 rounded-xl text-sm border border-slate-700">
                وضعیت سیستم: <span class="text-green-400 font-semibold">● آنلاین و فعال</span>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- بخش محصولات (کاتالوگ) -->
            <div class="lg:col-span-2 space-y-4">
                <div class="bg-white p-4 rounded-2xl shadow-sm flex items-center justify-between">
                    <input type="text" id="searchInput" placeholder="جستجو بر اساس نام خودرو یا کد قطعه (مثلا 5007 یا Sandero)..." 
                           class="w-full px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                </div>

                <div id="partsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for part in parts %}
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
                        <span>🤖 مشاور هوشمند قطعات (AI Assistant)</span>
                    </div>
                    <div id="chatMessages" class="flex-1 p-4 overflow-y-auto space-y-3 text-sm bg-slate-50">
                        <div class="bg-white p-3 rounded-xl shadow-xs border border-gray-200 text-slate-700">
                            سلام! من مشاور هوشمند کاتالوگ هستم. نام خودرو یا مشخصات قطعه مورد نظرتان را بپرسید تا بهترین گزینه را به شما پیشنهاد دهم.
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
        // جستجوی زنده در کاتالوگ
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

            fetch('/api/chat', {
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
            alert('سفارش شما با موفقیت ثبت شد و پیش‌فاکتور آماده ارسال به واتساپ شرکت گردید!');
            selectedItems = [];
            updateOrderUI();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, parts=PARTS_DATABASE)

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    user_msg = data.get('message', '').lower()
    
    # موتور جستجوی هوشمند متصل به کاتالوگ رنو
    matched = []
    for part in PARTS_DATABASE:
        if any(keyword in user_msg for keyword in part['name'].lower().split()) or part['code'] in user_msg:
            matched.append(part)
            
    if matched:
        reply = "بر اساس کاتالوگ قطعات رنو، موارد زیر با درخواست شما مطابقت دارند:\n<br>"
        for m in matched:
            reply += f"🔹 <b>{m['name']}</b> (کد: {m['code']}) - طول: {m['length']} - قطر: {m['diameter']}<br>"
        reply += "<br>مایلید این قطعات را به پیش‌فاکتور اضافه کنید؟"
    else:
        reply = "متاسفانه قطعه‌ای با این مشخصات در این بخش از کاتالوگ یافت نشد. می‌توانید نام مدل خودرو (مثل Megane, Clio, Sandero) یا کد قطعه را دقیق‌تر وارد کنید."
        
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)