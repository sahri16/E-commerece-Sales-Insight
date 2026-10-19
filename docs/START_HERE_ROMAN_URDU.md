# Sab se pehle yeh parhein

Yeh aapke upload kiye huay notebook project ka improved version hai. Ab aap browser mein sales, profit aur customers ka dashboard chala sakti hain. Coding ki daily zarurat nahi hogi.

## Kya required hai?

1. Laptop ya desktop: Windows, macOS ya Linux.
2. Python 3.11 ya 3.12; Python website se free install karein.
3. Chrome / Edge jaisa browser.
4. Pehli installation ke liye internet. Koi API key, paid subscription ya database required nahi.

Practical tor par 4 GB RAM aur takreeban 1 GB free storage rakhna theek hai; bari CSV zyada memory le sakti hai.

## Windows par sab se easy tareeqa

1. ZIP ko poora extract karein. ZIP ke andar se app na chalayein.
2. Python install karte waqt **Add Python to PATH** tick karein.
3. Extracted `Sales-Insight-Studio` folder mein `setup_windows.bat` double-click karein.
4. Installation complete honay ke baad `start_windows.bat` double-click karein.
5. Dashboard browser mein khul jayega. Nahi khulta to `http://localhost:8501` khol lein.
6. Black terminal window band na karein jab tak dashboard use karna ho. App band karne ke liye terminal mein Ctrl+C karein.
7. Agli dafa sirf `start_windows.bat` chalayein.

Yahan Linux/Python 3.12 par code aur dashboard tests kiye gaye hain. Windows launcher aapke computer par run karke verify karna baqi hai.

## Dashboard mein kya milega?

- Sales, profit, unique orders aur customers.
- Date, region, category aur segment ke filters.
- Har month ka sales/profit trend; alag years combine nahi honge.
- Loss mein janay wali sub-categories.
- Customers ki past spending aur repeat purchases.
- 1 se 12 month ka sales estimate, agar enough monthly data ho.
- Clean CSV, excluded rows, forecast CSV aur report ZIP download.

Forecast future ki guarantee nahi hai. Bohat choti CSV se forecast nahi banega. Latest month incomplete ho sakta hai is liye default par usay exclude kiya jata hai. Complete month ho to checkbox off kar sakti hain.

## Apni PixlyDecor sales ka data

`data/upload_template.csv` Excel ya kisi CSV editor mein khol kar structure dekhein. Is mein sirf demo invitation sales hain; aapki asli shop ke orders nahi.

Har line ke liye yeh columns required hain:

| Column | Kya bharna hai |
| --- | --- |
| Order ID | Order ka unique number |
| Order Date | Order ki date, behtar hai YYYY-MM-DD |
| Customer ID | Har customer ka stable ID |
| Sales | Is line ki total sale amount |
| Profit | Is line ka calculated profit |

Profit mein apni relevant fees aur costs consistently subtract karein. Sales ko profit samajh kar paste na karein. Agar profit available nahi, pehle calculate karna hoga; app khud Etsy fees nahi nikalti.

Region, Category, Sub-Category aur Segment optional hain. Digital invitations ke liye Ship Date / Ship Mode blank reh sakte hain.

CSV mein `$`, `PKR` ya comma-separated amounts use na karein: `1200.50` likhein. Ek file mein ek hi currency rakhein. Sidebar currency label amount convert nahi karta.

Etsy ka raw export direct import adapter is version mein nahi hai. Pehle relevant columns rename/map karein aur profit calculate karein. Phir sidebar se CSV upload karein aur matching date format choose karein.

Negative profit retain hota hai. Negative sales wali returns is version mein exclude hoti hain. Exact duplicate rows remove hoti hain; agar do identical order lines asal mein separate hon to unique Line ID column add karein.

## Original project mein kya problems theen?

CSV ka path wrong tha. Setup instructions aur requirements missing theen. Monthly graph mukhtalif years ke same months combine karta tha. Forecast chart mein future ke bajaye puranay data ki fitted values theen. Delivery aur customer lifetime value ke labels bhi accurate nahi thay. Yeh sab revised analysis mein correct kiya gaya hai.

## Asaan changes jo aap kar sakti hain

- Dashboard ka naam: `app.py` mein title change karein.
- Apne product names / categories: CSV mein change karein.
- Customer active/inactive rules: `analysis.py` mein 90 aur 180 days ki limits adjust karein.
- Graph colors: `app.py` mein Plotly chart settings change karein.

Baad mein fee calculator, Etsy column mapper aur returns handling add karna useful hoga. Yeh features abhi included nahi hain.

## Portfolio mein kaise use karein?

README English mein rewrite ki hai; setup aur explanation Roman Urdu mein yahan hai. Isay learning aur personal analysis ke liye use karein. CV mein wahi kaam likhein jo aap samajh kar explain kar sakti hain. Original project ki authorship apne naam claim na karein. Original ZIP `reference` folder mein preserved hai.
