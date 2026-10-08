// 👉 Anti-Detect Browser (Playwright Extra + Stealth Plugin)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

const SESSION_ID = process.env.IG_SESSION_ID || 'AAPKA_SESSION_ID_YAHAN_DALEIN';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

// 👉 NAYA LOGIC: Advanced Pop-up Handler (Har tarah ke pop-up handle karega)
async function handlePopups(page) {
    try {
        // Har possible dismiss button ka naam yahan add kar diya gaya hai
        const popupSelectors = [
            'button:has-text("Not Now")', 
            'button:has-text("Not now")', 
            'button:has-text("Cancel")',
            'button:has-text("Dismiss")',
            'button:has-text("Later")'
        ].join(', ');

        const popupBtn = page.locator(popupSelectors).first();
        
        // Sirf 3 second wait karega, agar koi pop-up hoga toh hata dega
        await popupBtn.waitFor({ state: 'visible', timeout: 3000 });
        console.log("🔔 Pop-up detected! Automatically clicking to dismiss...");
        await popupBtn.click({ force: true });
        await randomSleep(1500, 2500); // Click ke baad thoda time
    } catch (error) {
        // Koi popup nahi aaya to chup-chap aage badho bina kisi error ke
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
    let trackData = JSON.parse(fs.readFileSync(trackFile, 'utf-8'));

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
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await randomSleep(3200, 5600); 
        await handlePopups(page); 

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

            console.log("🔎 Clicking on Search...");
            await page.locator('svg[aria-label="Search"]').last().click({ force: true });
            await randomSleep(1800, 3100);

            await handlePopups(page);

            const searchInput = page.getByPlaceholder('Search');
            // Clear previous search (if any)
            await searchInput.fill(''); 
            
            // 👉 NAYA LOGIC: 100% Manual Typing Simulation (Bina copy-paste ke)
            console.log(`⌨️ Typing username manually: ${selectedUsername}...`);
            await searchInput.pressSequentially(selectedUsername, { 
                delay: Math.floor(Math.random() * 150) + 150 // Har character par 150ms-300ms ka keyboard type delay
            });
            await randomSleep(3500, 5800);

            console.log("🖱️ Clicking on User Profile...");
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
                
                await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                await randomSleep(2800, 4800); 
                currentHeight = await page.evaluate(() => document.body.scrollHeight);

                const links = await page.\$\$eval('a', anchors => {
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
            }
            
            console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);

            trackData[selectedUsername] = {
                last_processed: new Date().toISOString()
            };
            fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));
            
            // 👉 NAYA LOGIC: User Change Delay (6 se 10 second random)
            if (i < eligibleUsers.length - 1) {
                const interUserDelay = Math.floor(Math.random() * (10000 - 6000 + 1) + 6000); // 6000ms to 10000ms
                console.log(`\n⏳ Switching to next profile search in ${(interUserDelay/1000).toFixed(1)} seconds...`);
                await sleep(interUserDelay);
            }
        }

        // 👉 NAYA LOGIC: Jab sabhi user ka kaam khatam ho jaye, toh Home section par jao
        console.log(`\n🏠 All target users processed. Going back to Home feed for final human activity...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await handlePopups(page);

        // 👉 NAYA LOGIC: Home section par 20 se 45 second random delay & scrolling
        const homeScrollDuration = Math.floor(Math.random() * (45000 - 20000 + 1) + 20000); // 20000ms to 45000ms
        console.log(`💤 Spending ${(homeScrollDuration/1000).toFixed(1)} seconds randomly scrolling the home feed before closing...`);
        
        const startTime = Date.now();
        while (Date.now() - startTime < homeScrollDuration) {
            // Niche scroll karega
            await page.evaluate(() => window.scrollBy({ top: Math.random() * 500 + 300, behavior: 'smooth' }));
            await randomSleep(2000, 4000);
            
            // Asli insaan ki tarah kabhi kabhi thoda wapas upar bhi dekhega (30% chance)
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

    await browser.close();
    console.log(`\n🎉 Job Done! Automation Complete for today.`);
}

startScraping();
