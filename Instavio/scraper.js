const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 🔐 SESSION ID from GitHub Secrets
const SESSION_ID = process.env.IG_SESSION_ID;

if (!SESSION_ID) {
    console.error("❌ ERROR: GitHub Secrets se IG_SESSION_ID nahi mila!");
    process.exit(1);
}

// ⏳ Delay Functions
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');
    const trackFile = path.join(instavioDir, 'track.json');

    // Auto-create files if missing
    if (!fs.existsSync(usernamesFile)) {
        console.log("❌ usernames.txt nahi mili!");
        return;
    }
    if (!fs.existsSync(trackFile)) {
        fs.writeFileSync(trackFile, JSON.stringify({}, null, 4));
    }

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);
    let trackData = JSON.parse(fs.readFileSync(trackFile, 'utf-8'));

    let selectedUser = null;
    const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000; 
    const now = Date.now();

    // 🕒 1 Day = 1 Username Logic
    for (const user of usernames) {
        const lastProcessed = trackData[user]?.last_processed;
        if (!lastProcessed) {
            selectedUser = user; break;
        } else {
            const timePassed = now - new Date(lastProcessed).getTime();
            if (timePassed > THIRTY_DAYS_MS) {
                selectedUser = user; break;
            } else {
                console.log(`⏭️ User '${user}' cooldown mein hai. Skipped.`);
            }
        }
    }

    if (!selectedUser) {
        console.log("ℹ️ Aaj ke liye koi eligible username nahi bacha hai. Automation ruk gaya.");
        return; 
    }

    console.log(`\n======================================`);
    console.log(`🎯 Aaj ka target: ${selectedUser}`);
    
    // Auto-create User Folder & video.txt
    const userFolder = path.join(instavioDir, selectedUser);
    if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });
    
    const videoTxtPath = path.join(userFolder, 'video.txt');
    if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');

    const existingVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

    console.log("🚀 Starting Playwright Automation...");
    const browser = await chromium.launch({
        headless: true, // "false" karke real-time test kar sakte hain
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        recordVideo: { dir: userFolder, size: { width: 1280, height: 720 } },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    await context.addCookies([{
        name: 'sessionid',
        value: SESSION_ID,
        domain: '.instagram.com',
        path: '/',
        secure: true,
        httpOnly: true
    }]);

    const page = await context.newPage();
    let newLinksFoundTotal = 0;

    try {
        console.log("🌐 Going to Instagram Home Page...");
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        
        // 🧍‍♂️ HUMAN ACTION 1: Home page par aakar 3-4 second wait karna
        console.log("👀 Looking at home feed for 3-4 seconds...");
        await randomSleep(3000, 4000);

        // 🧍‍♂️ HUMAN ACTION 2: Home feed ko thoda upar-niche scroll karna
        console.log("📜 Scrolling home feed up and down slowly...");
        await page.evaluate(() => window.scrollBy({ top: 700, behavior: 'smooth' }));
        await randomSleep(2000, 3000);
        await page.evaluate(() => window.scrollBy({ top: -400, behavior: 'smooth' }));
        
        // 🧍‍♂️ HUMAN ACTION 3: 5 se 6 second wait before searching
        console.log("⏳ Waiting 5-6 seconds before clicking search...");
        await randomSleep(5000, 6000);

        console.log("🔎 Clicking Search icon...");
        await page.locator('svg[aria-label="Search"]').last().click();
        await randomSleep(2000, 3000);

        // ⌨️ HUMAN ACTION 4: Bina copy-paste kiye dheere-dheere typing karna
        console.log(`⌨️ Typing username slowly: ${selectedUser}...`);
        await page.getByPlaceholder('Search').pressSequentially(selectedUser, { 
            delay: Math.floor(Math.random() * 150) + 150 // Har character ke beech 150-300ms gap
        });
        
        console.log("⏳ Waiting for search results to load...");
        await randomSleep(3000, 4000);

        // 🧍‍♂️ HUMAN ACTION 5: Profile click karne se pehle exact 5 seconds wait
        console.log("⏳ Username mil gaya. Clicking profile in 5 seconds...");
        await sleep(5000);

        console.log("🖱️ Clicking User Profile...");
        const userProfileLink = page.locator(`a[href="/${selectedUser}/"]`).first();
        await userProfileLink.click();
        await page.waitForLoadState('networkidle');

        // 🧍‍♂️ HUMAN ACTION 6: Profile click karne ke baad exact 2 seconds wait
        console.log("⏳ Profile opened. Waiting 2 seconds before starting scroll capture...");
        await sleep(2000);

        console.log("📜 Starting Continuous Fast Scroll Engine & Live URL Capture...");
        let previousHeight = 0;
        let currentHeight = await page.evaluate(() => document.body.scrollHeight);
        let reachedOldVideo = false;

        // ⚡ FAST SCROLL + LIVE EXTRACTION LOGIC
        while (previousHeight !== currentHeight && !reachedOldVideo) {
            previousHeight = currentHeight;
            
            // 🎬 FAST SCROLL: Seedha page ke bottom tak scroll karega
            await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
            
            // ⏳ Minimal Sleep: Sirf nayi videos load hone ka wait (3 to 5 sec)
            console.log(`⏳ Scrolled to bottom. Waiting for new posts to load...`);
            await randomSleep(3000, 5000);

            currentHeight = await page.evaluate(() => document.body.scrollHeight);

            // 📥 LIVE CAPTURE: Wait khatam hote hi saare naye links copy kar lena
            const pageLinks = await page.$$eval('a', anchors => anchors.map(a => a.href));
            const videoLinks = pageLinks.filter(href => href.includes('/reel/') || href.includes('/p/'));
            
            let addedInThisScroll = 0;

            for (const link of videoLinks) {
                if (existingVideos.has(link)) {
                    // Agar purani video (jo 30 din pehle li thi) mil jaye to loop break ke liye flag set karein
                    reachedOldVideo = true; 
                } else {
                    // Naya URL turant text file mein save karein
                    fs.appendFileSync(videoTxtPath, `${link}\n`);
                    existingVideos.add(link); // Set me add karein taaki duplicate dobara save na ho
                    addedInThisScroll++;
                    newLinksFoundTotal++;
                }
            }

            console.log(`🔗 Copied ${addedInThisScroll} new URLs in this scroll. (Total new: ${newLinksFoundTotal})`);
            
            if (reachedOldVideo) {
                console.log(`🛑 Old video found! Stopping scroll. Only collected videos from the last 30 days.`);
                break;
            }
        }
        console.log("✅ Scrolling & Copying Complete.");

        // 📝 Track JSON update karna
        if (!trackData[selectedUser]) trackData[selectedUser] = {};
        trackData[selectedUser].last_processed = new Date().toISOString();
        trackData[selectedUser].total_videos_saved = existingVideos.size;
        fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));

        console.log(`💾 Activity saved in track.json. Browser closing...`);

    } catch (error) {
        console.error(`❌ Error during automation:`, error.message);
    } finally {
        await context.close(); 
        await browser.close();
    }
    
    console.log(`🎉 Job Done! Extracted ${newLinksFoundTotal} new video URLs for ${selectedUser}.`);
}

startScraping();
