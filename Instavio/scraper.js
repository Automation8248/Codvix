// 👉 Anti-Detect Browser (Playwright Extra + Stealth Plugin)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// 👉 Secrets & Variables
const SESSION_ID = process.env.IG_SESSION_ID || 'AAPKA_SESSION_ID_YAHAN_DALEIN';
const TG_TOKEN = process.env.TELEGRAM_FAIL_TOKEN;
const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!SESSION_ID || SESSION_ID === 'AAPKA_SESSION_ID_YAHAN_DALEIN') {
    console.error("❌ ERROR: IG_SESSION_ID valid secret nahi mila!");
    process.exit(1);
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

// 👉 Telegram Alert Function
async function sendTelegramAlert(errorMessage) {
    if (!TG_TOKEN || !TG_CHAT_ID) return;
    try {
        const text = `🚨 *Instavio Automation Failed*\n\n*Error:*\n${errorMessage}`;
        const url = `https://api.telegram.org/bot${TG_TOKEN}/sendMessage`;
        await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: TG_CHAT_ID, text: text, parse_mode: 'Markdown' })
        });
    } catch (e) {
        console.error("⚠️ Telegram alert bhejne mein error aaya:", e.message);
    }
}

// 👉 Advanced Pop-up Handler (With Human Logic: 5s + 7s Delay)
async function smartPopupHandler(page) {
    let isPopupHandled = false;

    // Phase 1: Try clicking natural buttons multiple times in case of stacked popups
    for (let i = 0; i < 3; i++) {
        try {
            const popupSelectors = [
                'button:has-text("Not Now")', 'button:has-text("Not now")', 
                'button:has-text("Cancel")', 'button:has-text("Dismiss")', 
                'button:has-text("Later")', 'button:has-text("No Thanks")',
                'button:has-text("No thanks")', 'button:has-text("Skip")',
                'button:has-text("Ignore")', 'button:has-text("Decline")'
            ].join(', ');

            const popupBtn = page.locator(popupSelectors).filter({ state: 'visible' }).first();
            
            if (await popupBtn.isVisible({ timeout: 2000 })) {
                console.log("🔔 Pop-up button detected! Clicking to dismiss...");
                await popupBtn.click({ force: true });
                isPopupHandled = true;
                
                console.log("⏳ Human Logic: Click karne ke baad 5 seconds wait kar raha hoon...");
                await randomSleep(4500, 5500);
            } else {
                break; // Agar aur koi button nahi hai toh loop tod do
            }
        } catch (error) {
            break;
        }
    }

    // Phase 2: CSS DOM Annihilator
    try {
        const removedOverlay = await page.evaluate(() => {
            const cssSelectors = [
                '[class*="rnep"]', '[id*="rnep"]', 
                '[role="dialog"]', '[role="presentation"]', 
                '.x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k', 
                'div[data-visualcompletion="ignore"]'
            ];
            let removed = false;
            document.querySelectorAll(cssSelectors.join(', ')).forEach(element => {
                if (element && element.id !== 'mount_0_0_0') {
                    element.remove();
                    removed = true;
                }
            });
            document.body.style.setProperty('overflow', 'auto', 'important');
            document.documentElement.style.setProperty('overflow', 'auto', 'important');
            return removed;
        });

        if (removedOverlay && !isPopupHandled) {
            console.log("🧹 Hidden popup/overlay CSS se hataya gaya.");
            isPopupHandled = true;
        }
    } catch (e) {}

    if (isPopupHandled) {
        console.log("⏳ Pop-up clear ho gaya. Aage badhne se pehle 7 seconds additional wait kar raha hoon...");
        await randomSleep(6500, 7500);
    }
}

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');
    const trackFile = path.join(instavioDir, 'track.json');
    const recordingsDir = path.join(instavioDir, 'Recordings'); 

    if (!fs.existsSync(usernamesFile)) return console.log("❌ usernames.txt nahi mili!");
    if (!fs.existsSync(trackFile)) fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    if (!fs.existsSync(recordingsDir)) fs.mkdirSync(recordingsDir, { recursive: true });

    let eligibleUsers = [];
    try {
        const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);
        if (usernames.length === 0) return console.log("ℹ️ usernames.txt khali hai.");

        let trackData = {};
        try {
            const rawData = fs.readFileSync(trackFile, 'utf-8');
            if (rawData.trim() !== '') trackData = JSON.parse(rawData);
        } catch (err) {
            fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
        }

        const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;
        const now = Date.now();

        for (const username of usernames) {
            if (trackData[username] && trackData[username].last_processed) {
                const timePassed = now - new Date(trackData[username].last_processed).getTime();
                if (timePassed < THIRTY_DAYS_MS) continue; 
            }
            eligibleUsers.push(username); 
        }

        if (eligibleUsers.length === 0) {
            return console.log("ℹ️ Aaj ke liye koi user bacha nahi hai. Sab cooldown me hain.");
        }
        
        console.log(`🎯 Targets for Today: ${eligibleUsers.length}`);

        const browser = await chromium.launch({
            headless: true, 
            args: ['--disable-blink-features=AutomationControlled', '--disable-infobars', '--no-sandbox']
        });

        const isManualRun = process.env.RECORD_VIDEO === 'true'; 

        // 👉 Dynamic Context Manager for Partial Recording
        let context = null;
        let page = null;
        let currentlyRecording = null;

        async function switchContext(needRecording) {
            if (currentlyRecording === needRecording && context !== null) return;
            
            if (context) {
                console.log(`🔄 Switching Browser Context for Recording State...`);
                await context.close(); // Video save process trigger hota hai
            }
            
            const contextOptions = {
                viewport: { width: 1280, height: 720 },
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale: 'en-US', timezoneId: 'Asia/Kolkata', colorScheme: 'dark'
            };

            if (needRecording && isManualRun) {
                console.log("🎥 Screen Recording is ON for this phase.");
                contextOptions.recordVideo = { dir: recordingsDir, size: { width: 1280, height: 720 } };
            } else {
                console.log("⚡ Screen Recording is OFF for this phase.");
            }

            context = await browser.newContext(contextOptions);
            await context.addCookies([{
                name: 'sessionid', value: SESSION_ID, domain: '.instagram.com', path: '/', secure: true, httpOnly: true
            }]);
            page = await context.newPage();
            currentlyRecording = needRecording;
        }

        // Initialize First Context
        await switchContext(eligibleUsers.length > 0); 
        
        console.log(`🌐 Going to Home page initially...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
        await randomSleep(4000, 6000); 
        await smartPopupHandler(page);

        // 👉 Scraping Loop (Continuous Search)
        for (let i = 0; i < eligibleUsers.length; i++) {
            const selectedUsername = eligibleUsers[i];
            
            // Record First 2 or Last 1
            const shouldRecord = (i === 0 || i === 1 || i === eligibleUsers.length - 1);
            await switchContext(shouldRecord);

            if (page.url() !== 'https://www.instagram.com/' && !page.url().includes('instagram.com/?')) {
                console.log(`🌐 Re-routing to Home page to start fresh Search for ${selectedUsername}...`);
                await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
                await randomSleep(3000, 5000);
                await smartPopupHandler(page);
            }

            console.log(`\n======================================`);
            console.log(`🔍 Processing User ${i + 1} of ${eligibleUsers.length}: [${selectedUsername}]`);

            const userFolder = path.join(instavioDir, selectedUsername);
            if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

            const videoTxtPath = path.join(userFolder, 'video.txt');
            if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
            const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

            console.log("🔎 Clicking on Search Icon...");
            try {
                const searchIcon = page.locator('svg[aria-label="Search"], span:has-text("Search")').filter({ state: 'visible' }).first();
                await searchIcon.click({ force: true, timeout: 5000 });
            } catch (err) {
                console.log("⚠️ Normal Search click timeout. Forcing JS DOM Click...");
                await page.evaluate(() => {
                    const searchSvg = document.querySelector('svg[aria-label="Search"]');
                    if (searchSvg) {
                        let clickable = searchSvg.closest('a') || searchSvg.closest('div[role="link"]') || searchSvg.closest('div[role="button"]') || searchSvg.parentElement;
                        if(clickable) clickable.click();
                    }
                });
            }
            
            await randomSleep(2500, 4000);
            await smartPopupHandler(page); 

            try {
                const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').filter({ state: 'visible' }).first();
                await searchInput.waitFor({ state: 'visible', timeout: 8000 });
                await searchInput.fill(''); 
                
                console.log(`⌨️ Typing username manually: ${selectedUsername}...`);
                await searchInput.pressSequentially(selectedUsername, { delay: Math.floor(Math.random() * 150) + 150 });
            } catch (err) {
                console.log("⚠️ Input field Playwright timeout. Forcing JS DOM Value Injection...");
                await page.evaluate((uname) => {
                    let inp = document.querySelector('input[placeholder*="Search"]') || document.querySelector('input[placeholder*="search"]');
                    if (inp) {
                        inp.value = '';
                        inp.focus();
                        document.execCommand('insertText', false, uname);
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }, selectedUsername);
            }
            
            await randomSleep(4500, 6500); 

            console.log("🖱️ Clicking on User Profile from Search Results...");
            try {
                const userProfileLink = page.locator(`a[href="/${selectedUsername}/"]`).filter({ state: 'visible' }).first();
                await userProfileLink.click({ force: true, timeout: 5000 });
            } catch (err) {
                 console.log("⚠️ Profile Link click timeout. Forcing JS DOM Click...");
                 await page.evaluate((uname) => {
                    const links = Array.from(document.querySelectorAll('a'));
                    const targetLink = links.find(a => a.href.includes(`/${uname}/`));
                    if(targetLink) targetLink.click();
                }, selectedUsername);
            }
            
            console.log("⏳ Waiting for profile load...");
            await page.waitForLoadState('networkidle');
            await randomSleep(3400, 5200);

            await smartPopupHandler(page);

            console.log("📜 Starting Live Fast Scrolling & Extraction...");
            let previousHeight = 0;
            let currentHeight = await page.evaluate(() => document.body.scrollHeight);
            let reachedOldVideo = false;
            let newlyCopiedThisSession = 0;
            const tempCopied = new Set(); 

            while (previousHeight !== currentHeight && !reachedOldVideo) {
                previousHeight = currentHeight;
                
                try {
                    const showMoreBtn = page.locator(':text-matches("Show more posts", "i")').filter({ state: 'visible' }).first();
                    if (await showMoreBtn.isVisible({ timeout: 1000 })) {
                        await showMoreBtn.click({ force: true });
                        await randomSleep(1500, 2500); 
                    }
                } catch (e) {}

                await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                await randomSleep(2800, 4800); 
                currentHeight = await page.evaluate(() => document.body.scrollHeight);

                const links = await page.$$eval('a', anchors => {
                    return anchors.map(a => a.href).filter(href => href.includes('/reel/') || href.includes('/p/'));
                });

                for (const link of links) {
                    if (oldSavedVideos.has(link)) {
                        console.log(`🛑 MATCH FOUND! (${link}). Pehle se copy kiya hua hai. Stopping scroll.`);
                        reachedOldVideo = true;
                        break;
                    }

                    if (!tempCopied.has(link)) {
                        tempCopied.add(link);
                        fs.appendFileSync(videoTxtPath, `${link}\n`); 
                        oldSavedVideos.add(link);
                        newlyCopiedThisSession++;
                    }
                }
                console.log(`🔗 Scrolled... New added for ${selectedUsername} so far: ${newlyCopiedThisSession}`);
                await smartPopupHandler(page); 
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);
            trackData[selectedUsername] = { last_processed: new Date().toISOString() };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            if (i < eligibleUsers.length - 1) {
                const interUserDelay = Math.floor(Math.random() * (10000 - 6000 + 1) + 6000); 
                console.log(`\n⏳ Switching to next profile search in ${(interUserDelay/1000).toFixed(1)} seconds... (NO Home Refresh)`);
                await sleep(interUserDelay);
                
                console.log(`🌐 Going back to Home page for next Search operation...`);
                await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
                await randomSleep(2000, 4000);
            }
        }
        
        // ==========================================
        // 🎬 POST SCRAPING ACTIVITIES (Reels Watching)
        // ==========================================
        console.log(`\n🏠 All targets done! Going to Home Feed and Refreshing...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await randomSleep(2500, 3500);
        await page.reload({ waitUntil: 'domcontentloaded' }); 
        await randomSleep(4000, 6000);
        await smartPopupHandler(page);

        console.log(`📱 Navigating to Reels section...`);
        await page.goto('https://www.instagram.com/reels/', { waitUntil: 'domcontentloaded' });
        await randomSleep(3000, 5000);
        await smartPopupHandler(page);

        const reelsToWatch = Math.floor(Math.random() * (7 - 5 + 1)) + 5;
        console.log(`🍿 Watching ${reelsToWatch} Reels randomly...`);

        for (let r = 1; r <= reelsToWatch; r++) {
            const watchTime = Math.floor(Math.random() * (8000 - 4500 + 1) + 4500);
            console.log(`👁️ Watching reel ${r}/${reelsToWatch} for ${(watchTime/1000).toFixed(1)} seconds...`);
            await sleep(watchTime);
            await page.evaluate(() => window.scrollBy(0, window.innerHeight));
            await smartPopupHandler(page);
        }
        console.log("✅ Reels watching complete.");

        console.log("✅ Automation finished successfully. (Session ID is SAFE)");

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
        await sendTelegramAlert(`Automation Crashed!\nReason: ${error.message}`);
        // 👉 FIX: Error aane par seedha script kill nahi karega, balki aage finally block me jane dega
        process.exitCode = 1; 
    } finally {
        // 👉 FIX: Chaahe error aaye ya success ho, Browser naturally close hoga, jisse VIDEO HAMESHA SAVE hogi
        if (context) await context.close(); 
        if (browser) await browser.close();
        if (isManualRun) {
            console.log(`🎥 Complete Screen Recording saved in 'Recordings' folder.`);
        }
    }
}

startScraping();
