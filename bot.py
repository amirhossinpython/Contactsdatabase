from rubpy import Client, filters
from rubpy.types import Update
import random
import re
from typing import List, Tuple

class PhoneBookBot:
    def __init__(self):
        self.bot = Client(name='Contactsdatabase')
        self.data_loaded = False
        self.phone_data: List[Tuple[str, str]] = []
        
        # ثبت هندلرها
        self.bot.on_message_updates(filters.text , filters.regex('^/start$'))(self.handle_start)
        self.bot.on_message_updates(filters.text , filters.regex('^/search'))(self.handle_search)
        self.bot.on_message_updates(filters.text)(self.handle_other_messages)

    def load_data(self, filename: str = 'output_clean.txt') -> bool:
      
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                raw_data = file.readlines()
            
            processed_data = []
            for line in raw_data:
               
                if not line.strip() or re.match(r'^[=📱🧑]', line.strip()):
                    continue
                
              
                match = re.match(r'^([+\d\s-]+)\t+(.+)$', line.strip())
                if match:
                    phone = match.group(1).strip()
                    name = match.group(2).strip()
                    processed_data.append((phone, name))
            
            self.phone_data = processed_data
            self.data_loaded = True
            return True
            
        except Exception as e:
            print(f"خطا در بارگذاری داده‌ها: {e}")
            return False

    async def handle_start(self, update: Update):
        """پردازش دستور /start"""
        if not self.data_loaded:
            if not self.load_data():
                await update.reply("❌ خطا در بارگذاری داده‌ها!")
                return
        
        if not self.phone_data:
            await update.reply("⚠️ هیچ داده‌ای یافت نشد!")
            return
        
      
        sample_size = min(5, len(self.phone_data))
        samples = random.sample(self.phone_data, sample_size)
        
       
        response = self.format_response(samples, "نمونه‌هایی از داده‌ها")
        await update.reply(response)

    async def handle_search(self, update: Update):
       
        if not self.data_loaded:
            await update.reply("لطفاً اول /start را بزنید تا داده‌ها بارگذاری شوند")
            return
        
        query = update.text.replace('/search', '').strip()
        if not query:
            await update.reply("⚠️ لطفاً پس از /search عبارت جستجو را وارد کنید")
            return
        
        results = []
        for phone, name in self.phone_data:
            if query.lower() in phone.lower() or query.lower() in name.lower():
                results.append((phone, name))
                if len(results) >= 10:  
                    break
        
        if not results:
            await update.reply(f"🔍 نتیجه‌ای برای '{query}' یافت نشد")
            return
        
        response = self.format_response(results, f"نتایج جستجو برای '{query}'")
        await update.reply(response)

    async def handle_other_messages(self, update: Update):
        """مدیریت سایر پیام‌ها"""
        await update.reply(
            "🤖 ربات دفترچه تلفن\n\n"
            "دستورات موجود:\n"
            "/start - نمایش نمونه‌هایی از داده‌ها\n"
            "/search [عبارت] - جستجو در نام و شماره‌ها"
        )

    def format_response(self, data: List[Tuple[str, str]], title: str) -> str:
        """فرمت‌بندی حرفه‌ای پاسخ"""
        header = f"📋 {title}\n\n"
        header += "📱 شماره\t\t🧑 نام (عبری)\n"
        header += "="*40 + "\n"
        
        body = ""
        for phone, name in data:
           
            phone_part = phone.ljust(15)
            body += f"{phone_part}\t{name}\n"
        
        return header + body

    def run(self):
        """اجرای ربات"""
        print("ربات در حال اجرا...")
        self.bot.run()

# اجرای ربات
if __name__ == "__main__":
    bot = PhoneBookBot()
    bot.run()
