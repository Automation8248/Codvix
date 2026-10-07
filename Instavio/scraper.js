const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Apne Session ID yahan set karein (Environment variable se ya direct)
const SESSION_ID = process.env.IG_SESSION_ID || '80592166108%3AO1XlkbG20p1jzK%3A23%3AAYkIwM3q0T5Eoul4Lr9H1AKKys1t2aMYmixUc-w2Xw';

// Human-like delay function
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function startScraping() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');

    if (!fs.existsSync(usernamesFile)) {
        console.log("❌ usernames.txt nahi mili!");
        return;
    }

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);

    if (usernames.length === 0) {
        console.log("ℹ️ usernames.txt khali hai.");
        return;
    }

    console.log("🚀 Starting Real-Browser Automation (Playwright)...");

    // 1. Asli Browser Launch Karna
    const browser = await chromium.launch({
        headless: true, // Ise 'false' karein agar aap apne PC par live browser open hote dekhna chahte hain
        args: ['--disable-blink-features=AutomationControlled'] // Bot detection se bachne ke liye
    });

    for (const username of usernames) {
        console.log(`\n======================================`);
        console.log(`🔍 Processing Username: ${username}`);
        
        const userFolder = path.join(instavioDir, username);
        if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

        // 🎥 2. Screen Recording Set Karna
        const context = await browser.newContext({
            viewport: { width: 1280, height: 720 },
            recordVideo: { 
                dir: userFolder, // Recording user ke folder mein save hogi
                size: { width: 1280, height: 720 }
            },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });

        // 🍪 Session Cookie Inject Karna (Bina password login)
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
            await randomSleep(3000, 5000);

            // 4. Search Bar par Click aur Type Karna
            console.log("🔎 Clicking on Search...");
            await page.locator('svg[aria-label="Search"]').last().click();
            await randomSleep(2000, 3000);

            console.log(`⌨️ Typing username: ${username}...`);
            // Insaan ki tarah dheere-dheere type karna (delay: 150ms per character)
            await page.getByPlaceholder('Search').fill(username);
            await randomSleep(4000, 6000); // Wait for search results to appear

            // 5. User ki Profile par Click karna
            console.log("🖱️ Clicking on User Profile...");
            const userProfileLink = page.locator(`a[href="/${username}/"]`).first();
            await userProfileLink.click();
            await page.waitForLoadState('networkidle');
            await randomSleep(3000, 5000);

            // 6. Scroll down till all videos are loaded
            console.log("📜 Scrolling down to load all videos. Please wait...");
            let previousHeight = 0;
            let currentHeight = await page.evaluate(() => document.body.scrollHeight);
            
            while (previousHeight !== currentHeight) {
                previousHeight = currentHeight;
                // Insaan ki tarah scroll
                await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                await randomSleep(3000, 5000); // Wait for new posts to load
                currentHeight = await page.evaluate(() => document.body.scrollHeight);
            }
            console.log("✅ Reached bottom of the profile. All posts loaded.");

            // 7. Saare Video/Post links Extract karna
            console.log("🔗 Extracting all post/video URLs...");
            const links = await page.$$eval('a', anchors => {
                return anchors
                    .map(a => a.href)
                    .filter(href => href.includes('/reel/') || href.includes('/p/'));
            });

            // Duplicates hatana
            const uniqueLinks = [...new Set(links)];
            console.log(`📌 Found ${uniqueLinks.length} URLs.`);

            // 8. video.txt Create aur Save Karna
            const videoTxtPath = path.join(userFolder, 'video.txt');
            fs.writeFileSync(videoTxtPath, uniqueLinks.join('\n'));
            console.log(`💾 Saved all URLs to: ${username}/video.txt`);

            // 9. Browser Context close karna taaki Screen Recording File Save ho jaye
            await context.close();
            console.log(`🎥 Screen Recording saved in ${username} folder (as .webm file).`);

        } catch (error) {
            console.error(`❌ Error during automation for ${username}:`, error.message);
            await context.close(); // Error aaye tab bhi video save ho jaye
        }
        
        // Ek user done hone par aaram karega
        console.log(`⏳ Waiting before moving to next user...`);
        await randomSleep(15000, 30000);
    }

    await browser.close();
    console.log(`\n🎉 All jobs done! Automation Complete.`);
}

startScraping();
