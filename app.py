import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TogelPredictor:
    def __init__(self):
        self.data_file = "togel_data.json"
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical togel data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.historical_data = json.load(f)
        else:
            self.historical_data = []
    
    def save_data(self, new_data):
        """Save new togel data"""
        self.historical_data.append({
            'date': datetime.now().isoformat(),
            'result': new_data
        })
        with open(self.data_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
    
    def frequency_analysis(self):
        """Analisis frekuensi kemunculan angka"""
        if not self.historical_data:
            return {}
        
        frequency = {}
        for entry in self.historical_data:
            result = str(entry['result'])
            for digit in result:
                if digit.isdigit():
                    frequency[digit] = frequency.get(digit, 0) + 1
        
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
    
    def statistical_analysis(self):
        """Analisis statistik pola angka"""
        if len(self.historical_data) < 10:
            return None
        
        numbers = []
        for entry in self.historical_data[-30:]:
            result = str(entry['result'])
            if len(result) == 4:
                numbers.append(int(result))
        
        if not numbers:
            return None
        
        return {
            'mean': np.mean(numbers),
            'std': np.std(numbers),
            'trend': 'naik' if numbers[-1] > numbers[-5] else 'turun'
        }
    
    def zigzag_pattern(self):
        """Analisis pola zigzag"""
        if len(self.historical_data) < 5:
            return []
        
        recent_data = [int(str(entry['result'])) for entry in self.historical_data[-10:]]
        pattern = []
        
        for i in range(1, len(recent_data)):
            if recent_data[i] > recent_data[i-1]:
                pattern.append('UP')
            else:
                pattern.append('DOWN')
        
        return pattern
    
    def probability_calculation(self):
        """Kalkulasi probabilitas berdasarkan data historis"""
        freq = self.frequency_analysis()
        total = sum(freq.values()) if freq else 1
        
        probabilities = {}
        for digit, count in freq.items():
            probabilities[digit] = round((count / total) * 100, 2)
        
        return probabilities
    
    def generate_4d_prediction(self):
        """Generate prediksi 4D (4 line)"""
        freq = self.frequency_analysis()
        stats = self.statistical_analysis()
        probs = self.probability_calculation()
        
        if not freq:
            # Default prediction jika tidak ada data
            return ['1234', '5678', '9012', '3456']
        
        # Ambil digit dengan frekuensi tertinggi
        top_digits = list(freq.keys())[:7]
        
        predictions = []
        for i in range(4):
            # Generate 4 digit number
            prediction = ''
            used_digits = set()
            
            for j in range(4):
                available_digits = [d for d in top_digits if d not in used_digits]
                if not available_digits:
                    available_digits = [str(np.random.randint(0, 10))]
                
                digit = np.random.choice(available_digits)
                prediction += digit
                used_digits.add(digit)
            
            predictions.append(prediction)
        
        return predictions
    
    def generate_bbfs(self):
        """Generate BBFS 7 digit"""
        freq = self.frequency_analysis()
        
        if not freq:
            return '1234567'
        
        # Ambil 7 digit dengan frekuensi tertinggi
        top_digits = list(freq.keys())[:7]
        
        # Pastikan ada 7 digit
        while len(top_digits) < 7:
            missing_digit = str(np.random.randint(0, 10))
            if missing_digit not in top_digits:
                top_digits.append(missing_digit)
        
        return ''.join(top_digits[:7])

# Initialize predictor
predictor = TogelPredictor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    keyboard = [
        [InlineKeyboardButton("🎯 Prediksi 4D", callback_data='predict_4d')],
        [InlineKeyboardButton("🔢 Generate BBFS", callback_data='generate_bbfs')],
        [InlineKeyboardButton("📊 Analisis Statistik", callback_data='show_stats')],
        [InlineKeyboardButton("📈 Input Data Baru", callback_data='input_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎲 *OVERCLOCK* 🎲
🎲 *BY : BANG ALE* 🎲

Selamat datang di Bot Prediksi Togel!
Bot ini menggunakan analisis:
• 📊 Statistik
• 🔄 Frekuensi  
• 🎯 Probabilitas
• 📈 Pola Zigzag

Pilih menu di bawah untuk mulai:
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'predict_4d':
        predictions = predictor.generate_4d_prediction()
        
        text = "🎯 *PREDIKSI 4D - 4 LINE*\n\n"
        for i, pred in enumerate(predictions, 1):
            text += f"Line {i}: `{pred}`\n"
        
        # Tambahkan analisis
        freq = predictor.frequency_analysis()
        if freq:
            text += f"\n📊 *Analisis Frekuensi:*\n"
            top_3 = list(freq.items())[:3]
            for digit, count in top_3:
                text += f"Angka {digit}: {count}x\n"
        
        keyboard = [[InlineKeyboardButton("🔄 Prediksi Ulang", callback_data='predict_4d')],
                   [InlineKeyboardButton("🏠 Menu Utama", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'generate_bbfs':
        bbfs = predictor.generate_bbfs()
        probs = predictor.probability_calculation()
        
        text = f"🔢 *BBFS 7 DIGIT*\n\n"
        text += f"BBFS: `{bbfs}`\n\n"
        
        if probs:
            text += "📊 *Probabilitas per Digit:*\n"
            for digit in bbfs:
                prob = probs.get(digit, 0)
                text += f"Digit {digit}: {prob}%\n"
        
        keyboard = [[InlineKeyboardButton("🔄 Generate Ulang", callback_data='generate_bbfs')],
                   [InlineKeyboardButton("🏠 Menu Utama", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'show_stats':
        freq = predictor.frequency_analysis()
        stats = predictor.statistical_analysis()
        zigzag = predictor.zigzag_pattern()
        
        text = "📊 *ANALISIS STATISTIK*\n\n"
        
        if freq:
            text += "🔄 *Frekuensi Angka:*\n"
            for digit, count in list(freq.items())[:5]:
                text += f"Angka {digit}: {count} kali\n"
            text += "\n"
        
        if stats:
            text += f"📈 *Statistik:*\n"
            text += f"Rata-rata: {stats['mean']:.0f}\n"
            text += f"Standar Deviasi: {stats['std']:.0f}\n"
            text += f"Trend: {stats['trend']}\n\n"
        
        if zigzag:
            text += f"📈 *Pola Zigzag (10 terakhir):*\n"
            text += " → ".join(zigzag[-5:])
        
        keyboard = [[InlineKeyboardButton("🏠 Menu Utama", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'input_data':
        text = "📈 *INPUT DATA BARU*\n\n"
        text += "Kirim hasil togel 4D terbaru untuk meningkatkan akurasi prediksi.\n\n"
        text += "Format: kirim 4 digit angka\n"
        text += "Contoh: `1234`"
        
        keyboard = [[InlineKeyboardButton("🏠 Menu Utama", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'main_menu':
        await start_menu(query)

async def start_menu(query):
    """Show main menu"""
    keyboard = [
        [InlineKeyboardButton("🎯 Prediksi 4D", callback_data='predict_4d')],
        [InlineKeyboardButton("🔢 Generate BBFS", callback_data='generate_bbfs')],
        [InlineKeyboardButton("📊 Analisis Statistik", callback_data='show_stats')],
        [InlineKeyboardButton("📈 Input Data Baru", callback_data='input_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎲 *OVERCLOCK* 🎲
🎲 *BY : BANG ALE* 🎲

Bot Prediksi Togel dengan analisis:
• 📊 Statistik • 🔄 Frekuensi  
• 🎯 Probabilitas • 📈 Pola Zigzag

Pilih menu di bawah:
    """
    
    await query.edit_message_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new data input"""
    text = update.message.text.strip()
    
    # Validasi input 4 digit
    if len(text) == 4 and text.isdigit():
        predictor.save_data(text)
        
        response = f"✅ *Data berhasil disimpan!*\n\n"
        response += f"Hasil: `{text}`\n"
        response += f"Total data: {len(predictor.historical_data)}\n\n"
        response += "Data ini akan digunakan untuk meningkatkan akurasi prediksi selanjutnya."
        
        keyboard = [
            [InlineKeyboardButton("🎯 Prediksi Sekarang", callback_data='predict_4d')],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            "❌ Format salah!\n\nKirim 4 digit angka (contoh: 1234)"
        )

def main():
    """Main function"""
    # Ganti dengan token bot Telegram Anda
    TOKEN = "7786703529:AAGr0NUfu2tYcQdYYpauCYWKzZs1Bzil-hE"
    
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_data_input))
    
    # Start bot
    print("🤖 OVERCLOCK started...")
    application.run_polling()

if __name__ == '__main__':
    main()
