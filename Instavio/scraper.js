const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 🔐 SESSION ID SECRET SE AA RAHA HAI (Public nahi hoga)
const SESSION_ID = process.env.IG_SESSION_ID;

if (!SESSION_ID) {
    console.error("❌ ERROR: GitHub Secrets se IG_SESSION_ID nahi mila!");
    process.exit(1);
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');
    const trackFile = path.join(instavioDir, 'track.json'); // 📝 Tracking File

    // Files check and initialization
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
    const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000; // 30 din milliseconds mein
    const now = Date.now();

    // 🕒 1. Ek eligible username select karna (30 days cooldown check)
    for (const user of usernames) {
        const lastProcessed = trackData[user]?.last_processed;
        
        if (!lastProcessed) {
            // Kabhi process nahi hua, ise select karo
            selectedUser = user;
            break;
        } else {
            const timePassed = now - new Date(lastProcessed).getTime();
            if (timePassed > THIRTY_DAYS_MS) {
                // 30 din ho chuke hain, ise wapas select karo
                selectedUser = user;
                break;
            } else {
                console.log(`⏭️ User '${user}' cooldown mein hai. (${Math.floor((THIRTY_DAYS_MS - timePassed)/(1000*60*60*24))} days bache hain).`);
            }
        }
    }

    if (!selectedUser) {
        console.log("ℹ️ Aaj ke liye koi eligible username nahi bacha hai. Sabhi 30-day cooldown mein hain. Automation ruk gaya.");
        return; // Bot yahan ruk jayega
    }

    console.log(`\n======================================`);
    console.log(`🎯 Aaj ka target (Only 1 user per day): ${selectedUser}`);
    
    // User setup
    const userFolder = path.join(instavioDir, selectedUser);
    if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });
    
    const videoTxtPath = path.join(userFolder, 'video.txt');
    if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');

    // Purani history read karna taaki pata chale purani video kahan se shuru hai
    const existingVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

    console.log("🚀 Starting Playwright Automation...");
    const browser = await chromium.launch({
        headless: true, // Testing ke liye ise false kar sakte hain
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        recordVideo: { dir: userFolder, size: { width: 1280, height: 720 } },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    await context.addCookies([{
        name: 'sessionid',
        value: SESSION_ID, // 🔐 Secrets se directly yahan feed ho raha hai
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
        await randomSleep(3000, 5000);

        console.log("🔎 Clicking Search and Typing...");
        await page.locator('svg[aria-label="Search"]').last().click();
        await randomSleep(2000, 3000);
        await page.getByPlaceholder('Search').fill(selectedUser);
        await randomSleep(4000, 6000); 

        console.log("🖱️ Opening User Profile...");
        const userProfileLink = page.locator(`a[href="/${selectedUser}/"]`).first();
        await userProfileLink.click();
        await page.waitForLoadState('networkidle');
        await randomSleep(3000, 5000);

        console.log("📜 Starting 6000ms Scroll Engine & Live Capture...");
        let previousHeight = 0;
        let currentHeight = await page.evaluate(() => document.body.scrollHeight);
        let reachedOldVideo = false;

        while (previousHeight !== currentHeight && !reachedOldVideo) {
            previousHeight = currentHeight;
            
            // 6000 MS (6 Seconds) Scrolling Sleep 
            await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
            console.log(`⏳ Scrolled. Waiting 6000ms for videos to load...`);
            await sleep(6000); // FIX 6000 ms as requested

            currentHeight = await page.evaluate(() => document.body.scrollHeight);

            // 📥 LIVE URL CAPTURE: Load hote hi URL nikalna
            const pageLinks = await page.$$eval('a', anchors => anchors.map(a => a.href));
            const videoLinks = pageLinks.filter(href => href.includes('/reel/') || href.includes('/p/'));
            
            let addedInThisScroll = 0;

            for (const link of videoLinks) {
                if (existingVideos.has(link)) {
                    // Agar purani video (jo 30 din pehle li thi) mil jaye to aage scroll rok do
                    reachedOldVideo = true; 
                } else {
                    // Naya URL turant save karo (Live Saving)
                    fs.appendFileSync(videoTxtPath, `${link}\n`);
                    existingVideos.add(link); // Set me add karo taaki dubara save na ho
                    addedInThisScroll++;
                    newLinksFoundTotal++;
                }
            }

            console.log(`🔗 Copied ${addedInThisScroll} new URLs in this scroll. (Total new: ${newLinksFoundTotal})`);
            
            if (reachedOldVideo) {
                console.log(`🛑 Old video found! Stopping scroll to only collect videos from the last 30 days.`);
                break;
            }
        }
        console.log("✅ Scrolling Complete.");

        // 📝 Update Activity in track.json
        if (!trackData[selectedUser]) trackData[selectedUser] = {};
        trackData[selectedUser].last_processed = new Date().toISOString();
        trackData[selectedUser].total_videos_saved = existingVideos.size;
        fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));

        console.log(`💾 Activity saved in track.json. Screen recording will now close and save.`);

    } catch (error) {
        console.error(`❌ Error during automation:`, error.message);
    } finally {
        await context.close(); 
        await browser.close();
    }
    
    console.log(`🎉 Today's Job Done! Added ${newLinksFoundTotal} new URLs for ${selectedUser}.`);
}

startScraping();
