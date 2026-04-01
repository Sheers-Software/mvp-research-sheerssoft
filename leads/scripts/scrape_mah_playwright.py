"""
MAH Playwright Scraper v4 — FINAL with exact ID-based selectors
DOM structure confirmed from browser inspection:
  h3.entry-title           → hotel name
  div.sp-blog-meta > ul > li > a → state, star rating, room count (text, not href)
  p#body_rpt_p_address_N   → address (with <br> separators)
  div.sp-contacts-list > ul
    li#body_rpt_li_phone_N  → plain text phone
    li#body_rpt_li_email_N  → plain text email
    li#body_rpt_li_globe_N  → plain text website URL
"""

import asyncio, json, re, os
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
MAH_URL = 'https://hotels.org.my/members'

CITY_MAP = {
    'Kuala Lumpur':'Kuala Lumpur','Selangor':'Petaling Jaya',
    'Penang':'George Town','Johor':'Johor Bahru','Sabah':'Kota Kinabalu',
    'Sarawak':'Kuching','Perak':'Ipoh','Kedah':'Langkawi',
    'Pahang':'Kuantan','Melaka':'Melaka','Negeri Sembilan':'Seremban',
    'Kelantan':'Kota Bharu','Terengganu':'Kuala Terengganu',
}
PRIORITY = {
    'Kuala Lumpur':1,'Selangor':2,'Penang':3,'Johor':4,'Sabah':5,
    'Sarawak':6,'Perak':7,'Melaka':8,'Negeri Sembilan':9,'Kedah':10,
}

# Use ID pattern to reliably extract indexed hotel data
EXTRACT_JS = """() => {
    const results = [];
    
    // MAH uses indexed IDs: body_rpt_li_phone_0, body_rpt_li_email_0, body_rpt_p_address_0, etc.
    // Find max index by looking for h3 count
    const h3s = document.querySelectorAll('h3.entry-title');
    const n = h3s.length;
    
    for (let i = 0; i < n; i++) {
        const h3 = h3s[i];
        const nameText = (h3.textContent || '').trim();
        if (!nameText) continue;
        
        // Address from <p id="body_rpt_p_address_i">
        const addrEl = document.getElementById(`body_rpt_p_address_${i}`);
        const address = addrEl ? addrEl.innerText.replace(/\\s*\\n\\s*/g, ', ').replace(/\\s{2,}/g,' ').trim() : '';
        
        // Phone from <li id="body_rpt_li_phone_i"> (plain text, strip icon text)
        const phoneEl = document.getElementById(`body_rpt_li_phone_${i}`);
        let phone = '';
        if (phoneEl) {
            // Remove icon text (icon uses <i> tag), just get text nodes
            const textNodes = [];
            phoneEl.childNodes.forEach(n => { if (n.nodeType === 3) textNodes.push(n.textContent.trim()); });
            phone = textNodes.join('').trim() || phoneEl.textContent.replace(/[^+0-9\\-\\s]/g,'').trim();
        }
        
        // Email from <li id="body_rpt_li_email_i">
        const emailEl = document.getElementById(`body_rpt_li_email_${i}`);
        let email = '';
        if (emailEl) {
            const textNodes = [];
            emailEl.childNodes.forEach(n => { if (n.nodeType === 3) textNodes.push(n.textContent.trim()); });
            email = textNodes.join('').trim() || '';
            // Also try <a> within it
            const emailLink = emailEl.querySelector('a');
            if (!email && emailLink) {
                email = (emailLink.href || '').replace('mailto:','').trim() || emailLink.textContent.trim();
            }
            // Text node fallback with regex
            if (!email) {
                const m = emailEl.textContent.match(/[\\w\\.\\-]+@[\\w\\.\\-]+\\.[a-z]{2,}/i);
                if (m) email = m[0];
            }
        }
        
        // Website from <li id="body_rpt_li_globe_i">
        const webEl = document.getElementById(`body_rpt_li_globe_${i}`);
        let website = '';
        if (webEl) {
            const textNodes = [];
            webEl.childNodes.forEach(n => { if (n.nodeType === 3 && n.textContent.trim()) textNodes.push(n.textContent.trim()); });
            website = textNodes.join('').trim();
            // Also try link
            const webLink = webEl.querySelector('a');
            if (!website && webLink) website = webLink.href || webLink.textContent.trim();
            // Ensure http prefix
            if (website && !website.startsWith('http')) website = 'https://' + website;
        }
        
        // State, star rating, rooms from div.sp-blog-meta > ul > li > a text
        let state='', starRating='', rooms='';
        const metaEl = h3.nextElementSibling;
        if (metaEl && metaEl.classList.contains('sp-blog-meta')) {
            const metaLink = metaEl.querySelector('a');
            if (metaLink) {
                const t = metaLink.textContent.trim();
                // Format: "Sarawak, Others (96 rooms)"
                const sm = t.match(/^([A-Za-z\\s]+?)(?:,|$)/); if (sm) state = sm[1].trim();
                const rm = t.match(/(\\d)\\s*Star|Orchid|Others|Associate/i); if (rm) starRating = rm[0].trim();
                const nm = t.match(/\\((\\d+)\\s*rooms?\\)/i); if (nm) rooms = nm[1];
            }
        }
        
        // Member ID from hotel name "(XXXX)"
        const midMatch = nameText.match(/\\((\\d+)\\)$/);
        const member_id = midMatch ? midMatch[1] : '';
        
        results.push({ hotel_name:nameText, member_id, state, star_rating:starRating, rooms, address, phone, email, website });
    }
    return results;
}"""

def cp(p):
    # Remove icon text — MAH phone sometimes has icon characters
    p = re.sub(r'[^\d\+\-\s]', '', str(p or ''))
    p = p.strip()
    if not p: return ''
    p = re.sub(r'[\s\-]','',p)
    if p.startswith('0') and len(p)>7: p='+60'+p[1:]
    elif p.startswith('60') and not p.startswith('+60') and len(p)>8: p='+'+p
    return p

def mob(p): return bool(re.match(r'^\+?601[0-9]',(p or '').replace(' ','')))

def score(h):
    s,f=0,[]
    star=h.get('star_rating',''); rooms=h.get('num_rooms') or 0; state=h.get('state','')
    if '3 Star' in star or '4 Star' in star: s+=3; f.append(star)
    elif star in ('Orchid','Others'): s+=1
    if rooms:
        if 50<=rooms<=300: s+=3; f.append(f'{rooms} rooms')
        elif 300<rooms<=400: s+=2
        elif rooms>400: s-=1
    p2=PRIORITY.get(state,20); s+=max(0,3-(p2//3))
    if h.get('email'): s+=1; f.append('Email')
    if h.get('is_mobile_whatsapp'): s+=2; f.append('WhatsApp')
    elif h.get('phone'): s+=1; f.append('Phone')
    if h.get('website'): s+=1
    h['icp_score']=s; h['icp_flags']=' | '.join(f)
    return h

def norm(raw):
    nr=(raw.get('hotel_name') or '').strip()
    member_id=raw.get('member_id','')
    if not member_id:
        mid=re.search(r'\((\d+)\)$',nr); member_id=mid.group(1) if mid else ''
    name=re.sub(r'\s*\(\d+\)$','',nr).strip().title()
    state=(raw.get('state') or '').strip()
    star=(raw.get('star_rating') or '').strip()
    rs=str(raw.get('rooms','')or''); rooms=int(rs) if rs.isdigit() else None
    phone=cp(raw.get('phone','')or'')
    em=(raw.get('email') or '').strip().lower()
    # Validate email
    if em and not re.match(r'^[\w\.\-\+]+@[\w\.\-]+\.\w{2,}$',em): em=''
    web=(raw.get('website') or '').strip()
    addr=(raw.get('address') or '').strip()
    # Ensure website starts with http
    if web and not web.startswith('http'): web='https://'+web
    # Extract postcode from address
    pc_m=re.search(r'\b(\d{5})\b',addr); pc=pc_m.group(1) if pc_m else ''
    city=CITY_MAP.get(state,state)
    for cn in ['Kuala Lumpur','Bukit Bintang','George Town','Johor Bahru','Kota Kinabalu','Kuching','Ipoh','Langkawi','Melaka','Seremban','Kuantan']:
        if cn.lower() in addr.lower(): city=cn; break
    mobile=mob(phone)
    h={
        'member_id':member_id,'hotel_name':name,'hotel_name_upper':nr.upper(),
        'state':state,'city':city,'star_rating':star,'num_rooms':rooms,
        'postcode':pc,'address':addr,'phone':phone,'is_mobile_whatsapp':mobile,
        'email':em,'website':web,'source':'MAH Directory',
        'google_found':False,'google_place_id':'','google_name':'',
        'google_address':'','google_phone':'','google_website':'',
        'google_maps_url':'','google_rating':'','google_reviews':'',
        'google_business_status':'','has_after_hours_gap':True,
        'whatsapp_number':phone if mobile else '',
        'whatsapp_source':'mah_directory' if mobile else '',
    }
    return score(h)

async def extract(page):
    for attempt in range(3):
        try:
            await page.wait_for_load_state('networkidle',timeout=15000)
            await asyncio.sleep(1)
            data=await page.evaluate(EXTRACT_JS)
            parsed=[norm(d) for d in data if d.get('hotel_name')]
            return parsed
        except Exception as e:
            print(f'    extract err (attempt {attempt}): {e}')
            await asyncio.sleep(2)
    return []

async def get_pages(page):
    try:
        n=await page.evaluate("()=>{const s=document.querySelector('#body_uc_page_ddl,select[id*=page]');return s?s.options.length:40;}")
        return int(n)
    except: return 40

async def nav_page(page, num):
    try:
        await page.wait_for_selector('#body_uc_page_ddl,select[id*=page]',timeout=8000)
        async with page.expect_navigation(wait_until='networkidle',timeout=20000):
            await page.select_option('#body_uc_page_ddl,select[id*=page]',str(num))
        return True
    except:
        try:
            async with page.expect_navigation(wait_until='networkidle',timeout=20000):
                await page.evaluate(f"__doPostBack('body_uc_page_ddl','{num}')")
            return True
        except: return False

async def run():
    all_hotels=[]; seen=set()
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox'])
        ctx=await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width':1280,'height':900}
        )
        page=await ctx.new_page()
        print(f'[{datetime.now():%H:%M:%S}] Loading MAH directory...')
        try: await page.goto(MAH_URL,wait_until='networkidle',timeout=30000)
        except Exception as e: print(f'ERROR: {e}'); await browser.close(); return []
        try:
            btn=await page.query_selector('input[type=submit][value*=Search],button[type=submit]')
            if btn:
                async with page.expect_navigation(wait_until='networkidle',timeout=15000):
                    await btn.click()
        except: pass
        total=await get_pages(page)
        print(f'Pages: {total}')
        h1=await extract(page)
        for h in h1:
            k=h.get('member_id') or h['hotel_name_upper']
            if k not in seen: seen.add(k); all_hotels.append(h)
        # Show sample to verify
        s=all_hotels[0] if all_hotels else {}
        print(f'  Page 1: {len(h1)} found → {len(all_hotels)} unique')
        print(f'  Sample: {s.get("hotel_name")} | Email:{s.get("email")} | Phone:{s.get("phone")} | Web:{s.get("website")}')
        for pn in range(2,total+1):
            print(f'  Page {pn}/{total}...',end=' ')
            if not await nav_page(page,pn): print('SKIP'); continue
            hotels=await extract(page)
            new=0
            for h in hotels:
                k=h.get('member_id') or h['hotel_name_upper']
                if k not in seen: seen.add(k); all_hotels.append(h); new+=1
            print(f'{len(hotels)} found, {new} new (total: {len(all_hotels)})')
            if pn%5==0:
                with open(os.path.join(OUTPUT_DIR,f'mah_final_cp_{pn}.json'),'w',encoding='utf-8') as f:
                    json.dump(all_hotels,f,indent=2,ensure_ascii=False)
            await asyncio.sleep(0.3)
        await browser.close()
    return all_hotels

def main():
    print('MAH Playwright Scraper v4 — exact ID selectors\n')
    hotels=asyncio.run(run())
    out=os.path.join(OUTPUT_DIR,'mah_raw.json')
    with open(out,'w',encoding='utf-8') as f: json.dump(hotels,f,indent=2,ensure_ascii=False)
    s34=sum(1 for h in hotels if any(s in h.get('star_rating','') for s in ['3 Star','4 Star']))
    em=sum(1 for h in hotels if h.get('email'))
    ph=sum(1 for h in hotels if h.get('phone'))
    wa=sum(1 for h in hotels if h.get('is_mobile_whatsapp'))
    wb=sum(1 for h in hotels if h.get('website'))
    print(f'\nSaved {len(hotels)} hotels')
    print(f'3-4★:{s34} | Email:{em} | Phone:{ph} | WhatsApp:{wa} | Website:{wb}')
    if hotels:
        import json as J
        print('\n--- SAMPLE hotel ---')
        print(J.dumps(hotels[0],indent=2))

if __name__=='__main__': main()
