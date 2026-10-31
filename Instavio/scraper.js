// 👉 Anti-Detect Browser (Playwright Extra + Stealth Plugin)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// 👉 Secrets & Variables
const SESSION_ID = process.env.IG_SESSION_ID;
const TG_TOKEN = process.env.TELEGRAM_FAIL_TOKEN;
const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!SESSION_ID) {
    console.error("❌ ERROR: IG_SESSION_ID secret nahi mila!");
    process.exit(1);
}

// 👉 Delays for Human Logic
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

// 👉 HUMAN LOGIC: ADVANCED MULTIPLE POP-UP HANDLER
async function smartPopupHandler(page) {
    let popupHandled = false;

    // Phase 1: Try clicking natural buttons (Aapka diya hua logic + 5s Delay)
    for (let i = 0; i < 2; i++) { // Loop in case of double popups
        try {
            const popupSelectors = [
                'button:has-text("Not Now")', 
                'button:has-text("Not now")', 
                'button:has-text("Cancel")',
                'button:has-text("Dismiss")',
                'button:has-text("Later")'
            ].join(', ');

            const popupBtn = page.locator(popupSelectors).first();
            
            // Wait for 3.5 seconds to see if popup appears
            await popupBtn.waitFor({ state: 'visible', timeout: 3500 });
            
            console.log("🔔 Pop-up detected! Automatically clicking to dismiss...");
            await popupBtn.click({ force: true });
            popupHandled = true;

            // 5 second delay after clicking as requested
            console.log("⏳ Human Logic: Click ke baad 5 seconds wait kar raha hoon...");
            await randomSleep(4500, 5500); 

        } catch (error) {
            break; // Agar 3.5s mein koi button nahi dikha, toh loop tod do
        }
    }

    // Phase 2: CSS DOM Annihilator (Agar button na ho aur koi hidden overlay bach gaya ho)
    try {
        const removedCount = await page.evaluate(() => {
            const cssSelectors = [
                '[class*="rnep"]', '[id*="rnep"]', 
                '[role="dialog"]', '[role="presentation"]', 
                '.x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k', 
                'div[data-visualcompletion="ignore"]'
            ];
            let count = 0;
            document.querySelectorAll(cssSelectors.join(', ')).forEach(element => {
                if (element && element.id !== 'mount_0_0_0') {
                    element.remove();
                    count++;
                }
            });

            document.body.style.setProperty('overflow', 'auto', 'important');
            document.documentElement.style.setProperty('overflow', 'auto', 'important');
            return count;
        });

        if (removedCount > 0) {
            popupHandled = true;
            console.log("🧹 Hidden pop-up/overlay ko safely delete kar diya gaya.");
        }
    } catch (error) {}

    // Pop-up band hone ke baad 7 second ka aaram (As requested)
    if (popupHandled) {
        console.log("⏳ Human Logic: Pop-up poori tarah hatne ke baad 7 seconds aaram kar raha hoon...");
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

        let context = null;
        let page = null;
        let currentlyRecording = null;

        async function switchContext(needRecording) {
            if (currentlyRecording === needRecording && context !== null) return;
            
            if (context) {
                console.log(`🔄 Switching Context to change Recording state...`);
                await context.close();
            }
            
            const contextOptions = {
                viewport: { width: 1280, height: 720 },
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale: 'en-US', timezoneId: 'Asia/Kolkata', colorScheme: 'dark'
            };

            if (needRecording) {
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

        for (let i = 0; i < eligibleUsers.length; i++) {
            const selectedUsername = eligibleUsers[i];
            
            // Logic: Record First 2 users (i=0, i=1) OR the Last user
            const shouldRecord = (i === 0 || i === 1 || i === eligibleUsers.length - 1);
            await switchContext(shouldRecord);

            console.log(`\n======================================`);
            console.log(`🔍 Processing User ${i + 1} of ${eligibleUsers.length}: [${selectedUsername}]`);

            const userFolder = path.join(instavioDir, selectedUsername);
            if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

            const videoTxtPath = path.join(userFolder, 'video.txt');
            if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
            const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

            console.log(`🌐 Going to Home page to start Search...`);
            await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
            await randomSleep(4000, 6000); // Thoda extra natural wait
            
            console.log("🛡️ Checking for pop-ups on Home Page...");
            await smartPopupHandler(page);

            console.log("🔎 Clicking on Search Icon...");
            const searchIcon = page.locator('svg[aria-label="Search"], span:has-text("Search")').last();
            await searchIcon.click({ force: true });
            await randomSleep(2500, 3500); // Slow human click delay

            const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').first();
            await searchInput.waitFor({ state: 'visible', timeout: 15000 });
            await searchInput.fill(''); 
            
            console.log(`⌨️ Typing username manually: ${selectedUsername}...`);
            // Slower typing to look like a human
            await searchInput.pressSequentially(selectedUsername, { 
                delay: Math.floor(Math.random() * 200) + 200 
            });
            await randomSleep(4500, 6500); // Wait for search results to load fully

            console.log("🖱️ Clicking on User Profile from Search Results...");
            const userProfileLink = page.locator(`a[href="/${selectedUsername}/"]`).first();
            await userProfileLink.click({ force: true });
            
            console.log("⏳ Waiting for profile to load completely...");
            await page.waitForLoadState('networkidle');
            await randomSleep(4000, 6000);

            console.log("🛡️ Checking for pop-ups before scrolling...");
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
                    const showMoreBtn = page.locator(':text-matches("Show more posts", "i")').first();
                    if (await showMoreBtn.isVisible({ timeout: 1000 })) {
                        await showMoreBtn.click({ force: true });
                        await randomSleep(2000, 3000); 
                    }
                } catch (e) {}

                await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                await randomSleep(2500, 4500); 
                currentHeight = await page.evaluate(() => document.body.scrollHeight);

                const links = await page.$$eval('a', anchors => {
                    return anchors.map(a => a.href).filter(href => href.includes('/reel/') || href.includes('/p/'));
                });

                for (const link of links) {
                    if (oldSavedVideos.has(link)) {
                        console.log(`🛑 MATCH FOUND! (${link}). Stopping scroll.`);
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
                console.log(`🔗 Copied so far: ${newlyCopiedThisSession}`);
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);
            trackData[selectedUsername] = { last_processed: new Date().toISOString() };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            if (i < eligibleUsers.length - 1) {
                console.log(`🏠 Going to Home page and Refreshing for next user loop...`);
                await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
                await randomSleep(2500, 3500);
                await page.reload({ waitUntil: 'domcontentloaded' });
                await randomSleep(4000, 6000);
                await smartPopupHandler(page);
            }
        }
        
        // ==========================================
        // 🎬 POST SCRAPING ACTIVITIES (Reels)
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
        }
        console.log("✅ Reels watching complete.");

        console.log("✅ Automation finished successfully. Closing browser. (Session ID is SAFE)");

        await context.close(); 
        await browser.close();

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
        await sendTelegramAlert(error.message);
        process.exit(1); 
    }
}

startScraping();
