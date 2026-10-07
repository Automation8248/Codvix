// 👉 Anti-Detect Browser (Playwright Extra + Stealth Plugin)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// 🔐 SESSION ID from GitHub Secrets
const SESSION_ID = process.env.IG_SESSION_ID;

if (!SESSION_ID) {
    console.error("❌ ERROR: GitHub Secrets se IG_SESSION_ID nahi mila!");
    process.exit(1);
}

// ⏳ True Random Delay Functions (Millisecond accuracy)
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');
    const trackFile = path.join(instavioDir, 'track.json'); 

    // Auto-create tracking file if missing
    if (!fs.existsSync(usernamesFile)) {
        console.log("❌ usernames.txt nahi mili! File create karke username add karein.");
        return;
    }
    
    if (!fs.existsSync(trackFile)) {
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    }

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);
    let trackData = JSON.parse(fs.readFileSync(trackFile, 'utf-8'));

    if (usernames.length === 0) {
        console.log("ℹ️ usernames.txt khali hai.");
        return;
    }

    let targetUsername = null;
    const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;
    const now = Date.now();

    // 🕒 1 Day = 1 Username Logic (30 Days Cooldown check)
    for (const username of usernames) {
        if (trackData[username] && trackData[username].last_processed) {
            const timePassed = now - new Date(trackData[username].last_processed).getTime();
            if (timePassed < THIRTY_DAYS_MS) {
                continue; // 30 din nahi hue, skip and check next user
            }
        }
        // Eligible user mil gaya!
        targetUsername = username;
        break; 
    }

    if (!targetUsername) {
        console.log("ℹ️ Aaj ke liye koi eligible username nahi bacha hai. Sab cooling period me hain. Automation ruk gaya.");
        return;
    }

    console.log(`\n======================================`);
    console.log(`🎯 Aaj ka Target Selected: ${targetUsername} (Only 1 user for today)`);
    console.log("🚀 Starting Stealth Browser Automation (Anti-Detect Mode)...");

    // 📁 Auto-create User Folder & video.txt
    const userFolder = path.join(instavioDir, targetUsername);
    if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

    // Purani video.txt read karna taaki repeat match ho sake
    const videoTxtPath = path.join(userFolder, 'video.txt');
    let oldSavedLinks = new Set();
    if (fs.existsSync(videoTxtPath)) {
        const existing = fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l);
        oldSavedLinks = new Set(existing);
    } else {
        fs.writeFileSync(videoTxtPath, ''); 
    }

    // 1. Asli Browser Launch Karna (Stealth applied)
    const browser = await chromium.launch({
        headless: true,
        args: ['--disable-blink-features=AutomationControlled'] 
    });

    // 🎥 2. Conditional Screen Recording Logic (Auto Run = Off, Manual Run = On)
    const isManualRun = process.env.RECORD_VIDEO === 'true'; // YML file se value aayegi
    
    const contextOptions = {
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    };

    if (isManualRun) {
        console.log("🎥 Manual Run Detected: Screen Recording is ON.");
        contextOptions.recordVideo = { 
            dir: userFolder,
            size: { width: 1280, height: 720 }
        };
    } else {
        console.log("⚡ Auto Run Detected: Screen Recording is OFF (Saving resources and space).");
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
        // 3. Instagram Home Page par jana
        console.log("🌐 Going to Instagram Home Page...");
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        
        // Random wait between 4s to 7s on home page
        console.log("⏳ Home page loaded. Waiting like a human...");
        await randomSleep(4123, 7234);

        console.log("📜 Randomly scrolling home feed...");
        await page.evaluate(() => window.scrollBy({ top: Math.random() * 800 + 400, behavior: 'smooth' }));
        await randomSleep(1890, 3120); 
        await page.evaluate(() => window.scrollBy({ top: -(Math.random() * 500 + 200), behavior: 'smooth' }));
        await randomSleep(2300, 4800); 

        // 4. Search Bar par Click aur Type Karna
        console.log("🔎 Clicking on Search...");
        await page.locator('svg[aria-label="Search"]').last().click();
        await randomSleep(1650, 3420); 

        console.log(`⌨️ Typing username: ${targetUsername}...`);
        await page.getByPlaceholder('Search').pressSequentially(targetUsername, { 
            delay: Math.floor(Math.random() * 200) + 120 // Har character pe random 120-320ms gap
        });
        
        await randomSleep(2130, 4560);

        // 5. User ki Profile par Click karna
        console.log("🖱️ Clicking on User Profile...");
        const userProfileLink = page.locator(`a[href="/${targetUsername}/"]`).first();
        await userProfileLink.click();
        
        console.log("⏳ Profile clicked. Waiting for page to load naturally...");
        await randomSleep(4230, 6890); // 4 se almost 7 sec ka random wait

        // 6. Scroll down and LIVE COPY Video URLs
        console.log("📜 Starting live scrolling and extracting URLs...");
        let previousHeight = 0;
        let currentHeight = await page.evaluate(() => document.body.scrollHeight);
        
        const copiedLinks = new Set();
        let totalCopied = 0;
        let reachedOldVideo = false;
        
        while (previousHeight !== currentHeight) {
            previousHeight = currentHeight;

            // URL Extract
            const linksOnPage = await page.$$eval('a', anchors => {
                return anchors.map(a => a.href).filter(href => href.includes('/reel/') || href.includes('/p/'));
            });

            let newlyAdded = 0;
            for (const link of linksOnPage) {
                // Check agar URL purane month wali history mein hai
                if (oldSavedLinks.has(link)) {
                    console.log(`🛑 Old video found! (${link}). Stoping scroll. 30 Days Limit Reached.`);
                    reachedOldVideo = true;
                    break;
                }

                // Check agar naya URL iss session me abhi tak copy nahi hua hai
                if (!copiedLinks.has(link)) {
                    copiedLinks.add(link);
                    fs.appendFileSync(videoTxtPath, `${link}\n`); // Live save to txt
                    newlyAdded++;
                    totalCopied++;
                }
            }

            if (newlyAdded > 0) {
                console.log(`🔗 Copied ${newlyAdded} new URLs. (Total saved: ${totalCopied})`);
            }

            if (reachedOldVideo) break;

            // Scroll with random distance and random sleep
            await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
            await randomSleep(3450, 6780); // 3.4s to 6.7s random wait per scroll
            currentHeight = await page.evaluate(() => document.body.scrollHeight);
        }
        
        console.log(`✅ Process complete for this profile. Total NAYE Unique URLs saved: ${totalCopied}`);

        // Track JSON update karna
        trackData[targetUsername] = {
            last_processed: new Date().toISOString(),
            total_new_videos_added: totalCopied
        };
        fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
        console.log(`📝 track.json updated. Next run for this user after 30 days.`);

        // 👉 NAYA LOGIC: Final Random Sleep Profile (1 to 3.2 Minutes) taaki Instagram AI pattern na pakad sake
        const endDelayProfiles = [
            62000, 75000, 88000, 94000, 105000, 112000, 126000, 133000, 142000, 151000,
            159000, 168000, 175000, 182000, 191000, 192000, 83000, 119000, 137000, 148000
        ]; // 20 different time delays
        
        const finalRandomDelay = endDelayProfiles[Math.floor(Math.random() * endDelayProfiles.length)];
        
        console.log(`\n💤 Human Final Break: Bot will rest for ${(finalRandomDelay / 1000 / 60).toFixed(2)} minutes before closing completely.`);
        await sleep(finalRandomDelay);

        await context.close();
        if (isManualRun) {
            console.log(`🎥 Screen Recording saved in ${targetUsername} folder (as .webm file).`);
        }

    } catch (error) {
        console.error(`❌ Error during automation for ${targetUsername}:`, error.message);
        await context.close(); 
    }

    await browser.close();
    console.log(`\n🎉 Job Done! Automation Complete for today.`);
}

startScraping();
