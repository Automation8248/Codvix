// 👉 Anti-Detect Browser Interface (Stealth Library)
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

const fs = require('fs');
const path = require('path');

// Fast Random Delay Functions (Ab koi bhi delay 9 second se upar nahi jayega)
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

// 👉 Ultimate DOM & CSS Pop-up Annihilator (Jad se Delete karna)
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
                if (element && element.id !== 'mount_0_0_0') {
                    element.remove();
                }
            });

            document.body.style.setProperty('overflow', 'auto', 'important');
            document.body.style.setProperty('position', 'static', 'important');
            document.documentElement.style.setProperty('overflow', 'auto', 'important');
            document.body.className = document.body.className.replace(/_a3gq|_abcm/g, ''); 
        });
        await randomSleep(500, 1500); // Fast wait
    } catch (error) {
        // Silent catch
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
        console.log("ℹ️ Aaj ke liye koi user bacha nahi hai.");
        return;
    }

    console.log(`\n======================================`);
    console.log(`🎯 Total Targets Selected for Today: ${eligibleUsers.length}`);
    console.log("🚀 Starting Ultimate Stealth Browser Automation (FAST MODE)...");

    const browser = await chromium.launch({
        headless: true, 
        args: [
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--ignore-certificate-errors',
            '--window-position=0,0',
            '--window-size=1280,720'
        ]
    });

    const isManualRun = process.env.RECORD_VIDEO === 'true'; 

    const contextOptions = {
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale: 'en-US',
        timezoneId: 'Asia/Kolkata',
        colorScheme: 'dark' 
    };

    if (isManualRun) {
        console.log("🎥 Manual Run Detected. Screen Recording ON.");
        contextOptions.recordVideo = { dir: recordingsDir, size: { width: 1280, height: 720 } };
    }

    const context = await browser.newContext(contextOptions);
    const page = await context.newPage();

    try {
        for (let i = 0; i < eligibleUsers.length; i++) {
            const selectedUsername = eligibleUsers[i];
            
            console.log(`\n======================================`);
            console.log(`🔍 Processing User ${i + 1} of ${eligibleUsers.length}: [${selectedUsername}]`);

            const userFolder = path.join(instavioDir, selectedUsername);
            if (!fs.existsSync(userFolder)) fs.mkdirSync(userFolder, { recursive: true });

            const videoTxtPath = path.join(userFolder, 'video.txt');
            if (!fs.existsSync(videoTxtPath)) fs.writeFileSync(videoTxtPath, '');
            const oldSavedVideos = new Set(fs.readFileSync(videoTxtPath, 'utf-8').split('\n').map(l => l.trim()).filter(l => l));

            const profileUrl = `https://www.instagram.com/${selectedUsername}/`;
            console.log(`🌐 Going directly to profile URL: ${profileUrl}`);
            
            try {
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
                    
                    // 👉 NAYA LOGIC: Check for "Show more posts" button
                    try {
                        const showMoreBtn = page.locator(':text-matches("Show more posts", "i")').first();
                        if (await showMoreBtn.isVisible({ timeout: 1000 })) {
                            console.log("👆 'Show more posts' button found! Clicking it...");
                            await showMoreBtn.click({ force: true });
                            await randomSleep(1500, 2500); // Click ke baad load hone ka chota wait
                        }
                    } catch (e) {
                        // Button nahi mila toh koi baat nahi, aage badho
                    }

                    // Scrolling
                    await page.evaluate(() => window.scrollBy(0, document.body.scrollHeight));
                    await randomSleep(2000, 3500); // Scroll ke baad 2 se 3.5 sec wait
                    currentHeight = await page.evaluate(() => document.body.scrollHeight);

                    const links = await page.\$\$eval('a', anchors => {
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
                    console.log(`🔗 Scrolled... New added for ${selectedUsername}: ${newlyCopiedThisSession}`);
                    
                    await destroyAllPopups(page);
                }
                
                console.log(`✅ Extraction Complete for ${selectedUsername}. Saved ${newlyCopiedThisSession} new URLs.`);

                trackData[selectedUsername] = {
                    last_processed: new Date().toISOString()
                };
                fs.writeFileSync(trackFile, JSON.stringify(trackData, null, 4));

            } catch (userError) {
                console.error(`⚠️ Error while processing ${selectedUsername}. Skipping to next. Details: ${userError.message}`);
            }
            
            if (i < eligibleUsers.length - 1) {
                // Max delay between users is now strictly under 9 seconds (4s to 8s)
                const interUserDelay = Math.floor(Math.random() * (8000 - 4000 + 1) + 4000); 
                console.log(`\n⏳ Switching to next profile in ${(interUserDelay/1000).toFixed(1)} seconds...`);
                await sleep(interUserDelay);
            }
        }

        console.log(`\n🏠 All target users processed. Going back to Home feed...`);
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded' });
        await destroyAllPopups(page); 

        // Home scroll duration is now Max 9 seconds (5s to 9s)
        const homeScrollDuration = Math.floor(Math.random() * (9000 - 5000 + 1) + 5000); 
        console.log(`💤 Spending ${(homeScrollDuration/1000).toFixed(1)} seconds on home feed before closing...`);
        
        const startTime = Date.now();
        while (Date.now() - startTime < homeScrollDuration) {
            await page.evaluate(() => window.scrollBy({ top: Math.random() * 500 + 300, behavior: 'smooth' }));
            await randomSleep(1500, 2500);
            await destroyAllPopups(page);
        }

    } catch (error) {
        console.error(`❌ Global Error during automation:`, error.message);
    } finally {
        await context.close(); 
        if (isManualRun) {
            console.log(`🎥 Complete Screen Recording saved in 'Recordings' folder.`);
        }
    }

    // Final delay is now Max 9 seconds (4s to 8.5s)
    const randomEndDelay = Math.floor(Math.random() * (8500 - 4000 + 1) + 4000); 
    console.log(`\n💤 Applying final delay of ${(randomEndDelay/1000).toFixed(2)} seconds...`);
    await sleep(randomEndDelay);

    await browser.close();
    console.log(`\n🎉 Job Done! Fast Stealth Automation Complete.`);
}

startScraping();
