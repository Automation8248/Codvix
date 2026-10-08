// 👉 Anti-Detect Browser (Playwright Extra + Stealth Plugin)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// Session ID ab optional ban gaya hai (Bina login bypass ke karan)
const SESSION_ID = process.env.IG_SESSION_ID || '';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

// 👉 NAYA LOGIC: Login Wall / Pop-up Bypass (DOM Manipulation)
async function bypassLoginWall(page) {
    try {
        console.log("🛡️ Attempting to remove Login Wall / Pop-ups via DOM manipulation...");
        await page.evaluate(() => {
            // 1. 'rnep' aur Instagram ke login overlays ko dhoondh kar delete karna
            const overlays = document.querySelectorAll('[class*="rnep"], [id*="rnep"], [role="presentation"], .x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1iyjqo2.xl56j7k');
            
            overlays.forEach(overlay => {
                // Check if it's likely a full-screen overlay block
                if (overlay && window.getComputedStyle(overlay).position === 'fixed') {
                    overlay.remove(); // Element delete kar diya
                }
            });

            // 2. Scrolling ko wapas On karna (Kyunki pop-up aane par IG scroll block kar deta hai)
            document.body.style.overflow = 'auto';
            document.body.style.position = 'static';
        });
        console.log("✅ Login Wall removed & scrolling enabled!");
        await randomSleep(1500, 2500); 
    } catch (error) {
        console.log("✅ No blocking wall found. Moving forward.");
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

    let trackData = {};
    if (!fs.existsSync(trackFile)) {
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    } else {
        try {
            const rawData = fs.readFileSync(trackFile, 'utf-8');
            if (rawData.trim() !== '') trackData = JSON.parse(rawData);
        } catch (err) {
            fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
        }
    }
    
    if (!fs.existsSync(recordingsDir)) fs.mkdirSync(recordingsDir, { recursive: true });

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);

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
        console.log("ℹ️ Aaj ke liye koi user bacha nahi hai. Sab cooldown me hain.");
        return;
    }

    console.log(`\n======================================`);
    console.log(`🎯 Total Targets Selected for Today: ${eligibleUsers.length}`);
    console.log("🚀 Starting Stealth Browser Automation...");

    const browser = await chromium.launch({
        headless: true, 
        args: ['--disable-blink-features=AutomationControlled']
    });

    const isManualRun = process.env.RECORD_VIDEO === 'true'; 

    const contextOptions = {
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    };

    if (isManualRun) {
        console.log("🎥 Manual Run Detected. Screen Recording ON.");
        contextOptions.recordVideo = { dir: recordingsDir, size: { width: 1280, height: 720 } };
    } else {
        console.log("⚡ Auto Run Detected. Screen Recording OFF.");
    }

    const context = await browser.newContext(contextOptions);
    
    // Agar Session ID hai toh inject karega, warna bina login bypass logic par depend karega
    if (SESSION_ID) {
        await context.addCookies([{
            name: 'sessionid',
            value: SESSION_ID,
            domain: '.instagram.com',
            path: '/',
            secure: true,
            httpOnly: true
        }]);
    }

    const page = await context.newPage();

    try {
        // Loop for all eligible users
        for (let i = 0; i < eligibleUsers.length; i++) {
            const selectedUsername = eligibleUsers[i];
            
            console.log(`\n======================================`);
            console.log(`🔍 Processing User ${i + 1} of ${eligibleUsers.length}: [${selectedUsername}]`);

            const userFolder = path.join(instavioDir, selectedUsername);
            if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

            const videoTxtPath = path.join(userFolder, 'video.txt');
            if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
            const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

            // 👉 NAYA LOGIC: DIRECT URL NAVIGATION
            const profileUrl = `https://www.instagram.com/${selectedUsername}/`;
            console.log(`🌐 Going directly to profile: ${profileUrl}`);
            await page.goto(profileUrl, { waitUntil: 'domcontentloaded' });
            
            console.log("⏳ Waiting for profile to load naturally...");
            await randomSleep(4000, 6500); 

            // 👉 NAYA LOGIC: Bypass Login Pop-ups / Intercepts via DOM removal
            await bypassLoginWall(page);

            console.log("📜 Starting Live Fast Scrolling & Extraction...");
            let previousHeight = 0;
            let currentHeight = await page.evaluate(() => document.body.scrollHeight);
            
            let reachedOldVideo = false;
            let newlyCopiedThisSession = 0;
            const tempCopied = new Set(); 

            while (previousHeight !== currentHeight && !reachedOldVideo) {
                previousHeight = currentHeight;
                
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
                
                // Har scroll ke baad bhi ek baar DOM bypass call kar lo (incase scrolling pe pop-up aaye)
                await bypassLoginWall(page);
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);

            trackData[selectedUsername] = {
                last_processed: new Date().toISOString()
            };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            if (i < eligibleUsers.length - 1) {
                const interUserDelay = Math.floor(Math.random() * (10000 - 6000 + 1) + 6000); // 6000ms to 10000ms
                console.log(`\n⏳ Switching to next profile search in ${(interUserDelay/1000).toFixed(1)} seconds...`);
                await sleep(interUserDelay);
            }
        }

        console.log(`\n🏠 All target users processed. Going back to Home feed for final human activity...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await bypassLoginWall(page);

        const homeScrollDuration = Math.floor(Math.random() * (45000 - 20000 + 1) + 20000); // 20000ms to 45000ms
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
        console.log("✅ Final home feed scrolling complete.");

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
    } finally {
        await context.close(); 
        if (isManualRun) {
            console.log(`🎥 Complete Screen Recording saved in 'Recordings' folder.`);
        }
    }

    const randomEndDelay = Math.floor(Math.random() * (210000 - 60000 + 1) + 60000); 
    console.log(`\n💤 Applying final human random end delay of ${(randomEndDelay/1000/60).toFixed(2)} minutes...`);
    await sleep(randomEndDelay);

    await browser.close();
    console.log(`\n🎉 Job Done! Automation Complete for today.`);
}

startScraping();
