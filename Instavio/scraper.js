// 👉 NAYA LOGIC: Anti-Detect Browser Interface (Stealth mode)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// Apne Session ID yahan set karein
const SESSION_ID = process.env.IG_SESSION_ID || 'AAPKA_SESSION_ID_YAHAN_DALEIN';

// 👉 NAYA LOGIC: Human Activity Simulation (Random Delays)
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');
    const trackFile = path.join(instavioDir, 'track.json'); // Tracking ke liye file

    if (!fs.existsSync(usernamesFile)) {
        console.log("❌ usernames.txt nahi mili!");
        return;
    }

    // track.json nahi hai to auto-create karega
    if (!fs.existsSync(trackFile)) {
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    }

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);
    let trackData = JSON.parse(fs.readFileSync(trackFile, 'utf-8'));

    if (usernames.length === 0) {
        console.log("ℹ️ usernames.txt khali hai.");
        return;
    }

    // 👉 NAYA LOGIC: 24 hrs me only 1 user select karega aur 30 days ka cooldown check karega
    let selectedUsername = null;
    const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;
    const now = Date.now();

    for (const username of usernames) {
        if (trackData[username] && trackData[username].last_processed) {
            const timePassed = now - new Date(trackData[username].last_processed).getTime();
            if (timePassed < THIRTY_DAYS_MS) {
                continue; // 30 din nahi hue, is username ko skip karo
            }
        }
        selectedUsername = username; // Eligible user mil gaya
        break; // Sirf ek hi user select karna hai, isliye loop yahan tod denge
    }

    if (!selectedUsername) {
        console.log("ℹ️ Aaj ke liye koi user bacha nahi hai. Sabhi 30-day cooldown me hain. Automation band ho raha hai.");
        return;
    }

    console.log(`\n======================================`);
    console.log(`🎯 Target Selected for Today: ${selectedUsername}`);
    console.log("🚀 Starting Stealth Browser Automation (Anti-Detect)...");

    const userFolder = path.join(instavioDir, selectedUsername);
    if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

    // video.txt auto create & read for matching
    const videoTxtPath = path.join(userFolder, 'video.txt');
    if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
    const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

    // 1. Asli Browser Launch Karna
    const browser = await chromium.launch({
        headless: true, 
        args: ['--disable-blink-features=AutomationControlled']
    });

    // 👉 NAYA LOGIC: Screen recording conditionally work karega (Jab manual run hoga)
    // Github actions me process.env.RECORD_VIDEO true bhejenge workflow_dispatch aane par
    const isManualRun = process.env.RECORD_VIDEO === 'true'; 

    const contextOptions = {
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    };

    if (isManualRun) {
        console.log("🎥 Manual Run Detected. Screen Recording ON.");
        contextOptions.recordVideo = { dir: userFolder, size: { width: 1280, height: 720 } };
    } else {
        console.log("⚡ Auto Run Detected. Screen Recording OFF (Saving memory).");
    }

    const context = await browser.newContext(contextOptions);

    // 🍪 Session Cookie Inject Karna 
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
        console.log("🌐 Going to Instagram Home Page...");
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await randomSleep(3200, 5600); // Random delay (Human Logic)

        console.log("🔎 Clicking on Search...");
        await page.locator('svg[aria-label="Search"]').last().click();
        await randomSleep(1800, 3100);

        console.log(`⌨️ Typing username: ${selectedUsername}...`);
        await page.getByPlaceholder('Search').pressSequentially(selectedUsername, { 
            delay: Math.floor(Math.random() * 150) + 150 // Typing delay
        });
        await randomSleep(3500, 5800);

        console.log("🖱️ Clicking on User Profile...");
        const userProfileLink = page.locator(`a[href="/${selectedUsername}/"]`).first();
        await userProfileLink.click();
        await page.waitForLoadState('networkidle');
        await randomSleep(3400, 5200);

        console.log("📜 Starting Live Fast Scrolling & Extraction...");
        let previousHeight = 0;
        let currentHeight = await page.evaluate(() => document.body.scrollHeight);
        
        let reachedOldVideo = false;
        let newlyCopiedThisSession = 0;
        const tempCopied = new Set(); // Prevent duplicate saving in same run

        // 👉 NAYA LOGIC: Jaldi-jaldi scroll & live copy. Old match hote hi stop.
        while (previousHeight !== currentHeight && !reachedOldVideo) {
            previousHeight = currentHeight;
            
            // Insaan ki tarah randomly scroll
            await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
            await randomSleep(2800, 4800); // 2.8 to 4.8 sec random pause
            currentHeight = await page.evaluate(() => document.body.scrollHeight);

            // Extract Live URLs
            const links = await page.$$eval('a', anchors => {
                return anchors.map(a => a.href).filter(href => href.includes('/reel/') || href.includes('/p/'));
            });

            for (const link of links) {
                if (oldSavedVideos.has(link)) {
                    console.log(`🛑 MATCH FOUND! (${link}). Pehle se exist karta hai. Scrolling stop kar rahe hain.`);
                    reachedOldVideo = true;
                    break;
                }

                if (!tempCopied.has(link)) {
                    tempCopied.add(link);
                    fs.appendFileSync(videoTxtPath, `${link}\n`); // Live Save to text
                    oldSavedVideos.add(link);
                    newlyCopiedThisSession++;
                }
            }
            console.log(`🔗 Scrolled and checking URLs... New added so far: ${newlyCopiedThisSession}`);
        }
        console.log("✅ Scrolling Complete.");
        console.log(`💾 Total ${newlyCopiedThisSession} new URLs saved in video.txt`);

        // 👉 NAYA LOGIC: Track user for 30 Days
        trackData[selectedUsername] = {
            last_processed: new Date().toISOString()
        };
        fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
        console.log(`📝 User ${selectedUsername} tracking data saved. 30-day cooling active.`);

        await context.close();
        if (isManualRun) {
            console.log(`🎥 Screen Recording saved in ${selectedUsername} folder.`);
        }

    } catch (error) {
        console.error(`❌ Error during automation for ${selectedUsername}:`, error.message);
        await context.close(); 
    }
    
    // 👉 NAYA LOGIC: Final random end delay (Vary total execution time between 1 to 3.5 minutes)
    // Taki daily script chalne ka pattern (exact same minute) record na ho Instagram par
    const randomEndDelay = Math.floor(Math.random() * (210000 - 60000 + 1) + 60000); 
    console.log(`💤 Applying final human random end delay of ${(randomEndDelay/1000/60).toFixed(2)} minutes to spoof execution total time...`);
    await sleep(randomEndDelay);

    await browser.close();
    console.log(`\n🎉 Job Done! Automation Complete for today.`);
}

startScraping();
