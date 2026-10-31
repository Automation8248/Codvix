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

// 👉 Ultimate DOM Pop-up Annihilator
async function destroyAllPopups(page) {
    try {
        await page.evaluate(() => {
            const popupSelectors = [
                '[class*="rnep"]', '[id*="rnep"]', 
                '[role="dialog"]', '[role="presentation"]', 
                '.x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k', 
                'div[data-visualcompletion="ignore"]'
            ];
            
            document.querySelectorAll(popupSelectors.join(', ')).forEach(element => {
                if (element && element.id !== 'mount_0_0_0') element.remove();
            });

            document.body.style.setProperty('overflow', 'auto', 'important');
            document.documentElement.style.setProperty('overflow', 'auto', 'important');
        });
        await randomSleep(500, 1500); 
    } catch (error) {}
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

        // 👉 Dynamic Context Manager (Record ON/OFF handle karne ke liye)
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

        // 👉 Scraping Loop
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

            const profileUrl = `https://www.instagram.com/${selectedUsername}/`;
            console.log(`🌐 Going directly to profile: ${profileUrl}`);
            await page.goto(profileUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
            await randomSleep(3000, 5000); 

            await destroyAllPopups(page);

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
                        await randomSleep(1500, 2500); 
                    }
                } catch (e) {}

                await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                await randomSleep(2000, 3500); 
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
                await destroyAllPopups(page);
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);
            trackData[selectedUsername] = { last_processed: new Date().toISOString() };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            if (i < eligibleUsers.length - 1) {
                const interUserDelay = Math.floor(Math.random() * (8000 - 4000 + 1) + 4000); 
                console.log(`⏳ Switching to next profile in ${(interUserDelay/1000).toFixed(1)} seconds...`);
                await sleep(interUserDelay);
            }
        }

        // ==========================================
        // 🎬 POST SCRAPING ACTIVITIES (Last user context = Recording ON)
        // ==========================================
        
        console.log(`\n🏠 All targets done! Going to Home Feed and Refreshing...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await randomSleep(2000, 3000);
        await page.reload({ waitUntil: 'domcontentloaded' }); // Refresh Home Page
        await randomSleep(3000, 5000);
        await destroyAllPopups(page);

        console.log(`📱 Navigating to Reels section...`);
        await page.goto('https://www.instagram.com/reels/', { waitUntil: 'domcontentloaded' });
        await randomSleep(2000, 4000);
        await destroyAllPopups(page);

        // 👉 Watch 5 to 7 Reels
        const reelsToWatch = Math.floor(Math.random() * (7 - 5 + 1)) + 5;
        console.log(`🍿 Watching ${reelsToWatch} Reels randomly...`);

        for (let r = 1; r <= reelsToWatch; r++) {
            const watchTime = Math.floor(Math.random() * (8000 - 4000 + 1) + 4000);
            console.log(`👁️ Watching reel ${r}/${reelsToWatch} for ${(watchTime/1000).toFixed(1)} seconds...`);
            await sleep(watchTime);
            await page.evaluate(() => window.scrollBy(0, window.innerHeight));
        }
        console.log("✅ Reels watching complete.");

        // Logout logic yahan se hata diya gaya hai. Session ab safe rahega.
        console.log("✅ Automation finished successfully. Closing browser.");

        await context.close(); 
        await browser.close();

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
        await sendTelegramAlert(error.message);
        process.exit(1); 
    }
}

startScraping();
