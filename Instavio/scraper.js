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
async function handlePopups(page) {
    let isPopupHandled = false;
    try {
        const popupSelectors = [
            'button:has-text("Not Now")', 
            'button:has-text("Not now")', 
            'button:has-text("Cancel")',
            'button:has-text("Dismiss")',
            'button:has-text("Later")'
        ].join(', ');

        const popupBtn = page.locator(popupSelectors).first();
        
        await popupBtn.waitFor({ state: 'visible', timeout: 3500 });
        console.log("🔔 Pop-up detected! Automatically clicking to dismiss...");
        await popupBtn.click({ force: true });
        isPopupHandled = true;

        console.log("⏳ Human Logic: Click karne ke baad 5 seconds wait kar raha hoon...");
        await randomSleep(4500, 5500); 
    } catch (error) {
        // Koi button wala popup nahi aaya
    }

    // Safety layer: Hidden overlays/popups ko CSS se hatana
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

    // Pop-up handle hone ke baad additional 7 seconds wait
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

    if (!fs.existsSync(usernamesFile)) {
        console.log("❌ usernames.txt nahi mili!");
        return;
    }

    if (!fs.existsSync(trackFile)) {
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    }
    
    if (!fs.existsSync(recordingsDir)) fs.mkdirSync(recordingsDir, { recursive: true });

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);
    
    // 👉 FIX: JSON ko safe tareeqe se read karna
    let trackData = {};
    try {
        const rawData = fs.readFileSync(trackFile, 'utf-8');
        if (rawData.trim() !== '') {
            trackData = JSON.parse(rawData);
        }
    } catch (err) {
        console.log("⚠️ track.json file ka format galat tha ya corrupt thi. Isko auto-fix kar raha hoon...");
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
        trackData = {};
    }

    if (usernames.length === 0) {
        console.log("ℹ️ usernames.txt khali hai.");
        return;
    }

    let eligibleUsers = [];
    const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;
    const now = Date.now();

    for (const username of usernames) {
        if (trackData[username] && trackData[username].last_processed) {
            const timePassed = now - new Date(trackData[username].last_processed).getTime();
            if (timePassed < THIRTY_DAYS_MS) {
                console.log(`⏭️ '${username}' abhi 30-day cooldown me hai. Skipping...`);
                continue; 
            }
        }
        eligibleUsers.push(username); 
    }

    if (eligibleUsers.length === 0) {
        console.log("ℹ️ Aaj ke liye koi user bacha nahi hai. Sab cooldown me hain. Automation band ho raha hai.");
        return;
    }

    console.log(`\n======================================`);
    console.log(`🎯 Total Targets Selected for Today: ${eligibleUsers.length}`);
    console.log("🚀 Starting Stealth Browser Automation...");

    const browser = await chromium.launch({
        headless: true, 
        args: ['--disable-blink-features=AutomationControlled', '--disable-infobars', '--no-sandbox']
    });

    // Pehle 2 aur aakhiri 1 record karne ka logic (Using Record Video env)
    const isManualRun = process.env.RECORD_VIDEO === 'true'; 

    const contextOptions = {
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    };

    if (isManualRun) {
        console.log("🎥 Screen Recording ON.");
        contextOptions.recordVideo = { dir: recordingsDir, size: { width: 1280, height: 720 } };
    } else {
        console.log("⚡ Auto Run Detected. Screen Recording OFF.");
    }

    const context = await browser.newContext(contextOptions);
    
    await context.addCookies([{
        name: 'sessionid',
        value: SESSION_ID,
        domain: '.instagram.com',
        path: '/',
        secure: true,
        httpOnly: true
    }]);

    const page = await context.newPage();

    try {
        console.log("🌐 Going to Instagram Home Page (Only Once)...");
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
        await randomSleep(4000, 6000); 
        await handlePopups(page); 

        // 👉 Loop for all eligible users (Search Bar Continuous Loop)
        for (let i = 0; i < eligibleUsers.length; i++) {
            const selectedUsername = eligibleUsers[i];
            
            console.log(`\n======================================`);
            console.log(`🔍 Processing User ${i + 1} of ${eligibleUsers.length}: [${selectedUsername}]`);

            const userFolder = path.join(instavioDir, selectedUsername);
            if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

            const videoTxtPath = path.join(userFolder, 'video.txt');
            if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
            const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

            console.log("🔎 Clicking on Search Icon...");
            // Use robust search icon locator
            const searchIcon = page.locator('svg[aria-label="Search"], span:has-text("Search")').last();
            await searchIcon.click({ force: true });
            await randomSleep(2000, 3500);

            await handlePopups(page);

            // Wait for search input to appear properly
            const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').first();
            await searchInput.waitFor({ state: 'visible', timeout: 10000 }).catch(() => console.log("⏳ Search box wait..."));
            await searchInput.fill(''); // Clear previous search
            
            console.log(`⌨️ Typing username manually: ${selectedUsername}...`);
            await searchInput.pressSequentially(selectedUsername, { 
                delay: Math.floor(Math.random() * 150) + 150 
            });
            await randomSleep(4000, 6000); // Wait for results to load

            console.log("🖱️ Clicking on User Profile from Search Results...");
            const userProfileLink = page.locator(`a[href="/${selectedUsername}/"]`).first();
            await userProfileLink.click({ force: true });
            await page.waitForLoadState('networkidle');
            await randomSleep(3400, 5200);

            await handlePopups(page); 

            console.log("📜 Starting Live Fast Scrolling & Extraction...");
            let previousHeight = 0;
            let currentHeight = await page.evaluate(() => document.body.scrollHeight);
            
            let reachedOldVideo = false;
            let newlyCopiedThisSession = 0;
            const tempCopied = new Set(); 

            while (previousHeight !== currentHeight && !reachedOldVideo) {
                previousHeight = currentHeight;
                
                // Show more posts button logic
                try {
                    const showMoreBtn = page.locator(':text-matches("Show more posts", "i")').first();
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
                        fs.appendFileSync(videoTxtPath, `${link}\n`); // Live Save
                        oldSavedVideos.add(link);
                        newlyCopiedThisSession++;
                    }
                }
                console.log(`🔗 Scrolled... New added for ${selectedUsername} so far: ${newlyCopiedThisSession}`);
                await handlePopups(page); // Extract karte waqt agar popup aaye
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);

            trackData[selectedUsername] = {
                last_processed: new Date().toISOString()
            };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            if (i < eligibleUsers.length - 1) {
                const interUserDelay = Math.floor(Math.random() * (10000 - 6000 + 1) + 6000); 
                console.log(`\n⏳ Switching to next profile search in ${(interUserDelay/1000).toFixed(1)} seconds... (NO Home Refresh)`);
                await sleep(interUserDelay);
                // Script seedha wapas upar loop mein jayegi aur current profile se hi naya search karegi
            }
        }

        // ==========================================
        // 🎬 LAST MEIN HOME FEED SCROLL KARNA
        // ==========================================
        console.log(`\n🏠 All target users processed. Going back to Home feed for final human activity...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await handlePopups(page);

        const homeScrollDuration = Math.floor(Math.random() * (35000 - 20000 + 1) + 20000); // 20-35 seconds
        console.log(`💤 Spending ${(homeScrollDuration/1000).toFixed(1)} seconds randomly scrolling the home feed before closing...`);
        
        const startTime = Date.now();
        while (Date.now() - startTime < homeScrollDuration) {
            await page.evaluate(() => window.scrollBy({ top: Math.random() * 500 + 300, behavior: 'smooth' }));
            await randomSleep(2000, 4000);
            
            if (Math.random() > 0.7) {
                await page.evaluate(() => window.scrollBy({ top: -(Math.random() * 300 + 100), behavior: 'smooth' }));
                await randomSleep(1500, 2500);
            }
        }
        console.log("✅ Final home feed scrolling complete. Safe Exit.");

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
        await sendTelegramAlert(`Automation Crashed!\nReason: ${error.message}`);
        process.exit(1);
    } finally {
        await context.close(); 
        if (isManualRun) {
            console.log(`🎥 Complete Screen Recording saved in 'Recordings' folder.`);
        }
    }

    await browser.close();
    console.log(`\n🎉 Job Done! Automation Complete for today.`);
}

startScraping();
