const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

// GitHub secrets se secure credentials fetch karna
const SESSION_ID = process.env.IG_SESSION_ID;
const ELITE_CLOUD_API_KEY = process.env.ELITE_CLOUD_API_KEY; 

// Instagram Headers (Real browser jaisa dikhne ke liye)
const headers = {
    'Cookie': `sessionid=${SESSION_ID}`,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'x-ig-app-id': '936619743392459'
};

// Sleep / Delay function (Anti-Ban System)
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Instagram se user ki videos nikalna
async function getUserVideos(username) {
    try {
        const url = `https://i.instagram.com/api/v1/users/web_profile_info/?username=${username}`;
        const response = await axios.get(url, { headers });
        const edges = response.data.data.user.edge_owner_to_timeline_media.edges;
        
        let videos = [];
        for (let edge of edges) {
            if (edge.node.is_video) {
                videos.push({
                    shortcode: edge.node.shortcode,
                    video_url: edge.node.video_url,
                    post_url: `https://www.instagram.com/reel/${edge.node.shortcode}/` // Video ka URL save karne ke liye
                });
            }
        }
        return videos;
    } catch (error) {
        console.error(`❌ Error fetching profile ${username}:`, error.message);
        return [];
    }
}

// Video Download Function
async function downloadVideo(videoUrl, savePath) {
    const writer = fs.createWriteStream(savePath);
    const response = await axios({
        url: videoUrl,
        method: 'GET',
        responseType: 'stream'
    });
    response.data.pipe(writer);
    return new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
    });
}

// ☁️ ShreeCloudStorage Upload Function
async function uploadToShreeCloud(filePath) {
    const uploadUrl = 'https://shreecloud.up.railway.app/api/v1/upload';
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));

    try {
        console.log(`☁️ Uploading ${path.basename(filePath)} to Cloud...`);
        const response = await axios.post(uploadUrl, form, {
            headers: {
                'X-API-Key': ELITE_CLOUD_API_KEY, // User ka bataya hua Secret Token Name
                ...form.getHeaders()
            },
            maxBodyLength: Infinity,
            maxContentLength: Infinity
        });
        
        console.log(`☁️✅ Upload Successful! Server Data:`, response.data);
        return true;
    } catch (error) {
        console.error(`☁️❌ Upload Failed:`, error.response ? error.response.data : error.message);
        return false;
    }
}

// Main Automation Engine
async function startAutomation() {
    const instavioDir = __dirname;
    const usernamesFile = path.join(instavioDir, 'usernames.txt');

    // Agar usernames.txt nahi hai, to ise khud bana dega (Empty)
    if (!fs.existsSync(usernamesFile)) {
        console.log("⚠️ usernames.txt nahi mili. Automatic create kar raha hoon...");
        fs.writeFileSync(usernamesFile, '');
        console.log("✅ usernames.txt created. Kripya isme username add karein aur dubara run karein.");
        return;
    }

    const usernames = fs.readFileSync(usernamesFile, 'utf-8').split('\n').map(u => u.trim()).filter(u => u);

    if (usernames.length === 0) {
        console.log("ℹ️ usernames.txt khali hai. Koi username add nahi kiya gaya.");
        return;
    }

    for (const username of usernames) {
        console.log(`\n======================================`);
        console.log(`🔍 Processing Username: ${username}`);
        
        // 1. Username ka Folder Automatic Create Karna (Agar nahi hai)
        const userFolder = path.join(instavioDir, username);
        if (!fs.existsSync(userFolder)) {
            fs.mkdirSync(userFolder, { recursive: true });
            console.log(`📁 Folder created for: ${username}`);
        }

        // 2. history.txt Automatic Create Karna (Agar nahi hai)
        const historyFile = path.join(userFolder, 'history.txt');
        if (!fs.existsSync(historyFile)) {
            fs.writeFileSync(historyFile, '');
            console.log(`📄 history.txt created in ${username} folder`);
        }

        // History read karna taaki repeat na ho
        let history = fs.readFileSync(historyFile, 'utf-8').split('\n').map(l => l.trim()).filter(l => l);

        const videos = await getUserVideos(username);
        console.log(`📌 Found ${videos.length} video(s) for ${username}.`);
        let downloadedCount = 0;

        for (const video of videos) {
            // URL repeat check karne ka logic
            if (history.includes(video.post_url)) {
                console.log(`⏭️ Video URL [${video.post_url}] already history mein hai. Skipping...`);
                continue;
            }

            const videoPath = path.join(userFolder, `${video.shortcode}.mp4`);

            try {
                // Step 1: Download
                console.log(`⬇️ Downloading Video: ${video.shortcode}...`);
                await downloadVideo(video.video_url, videoPath);
                console.log(`✅ Downloaded locally.`);
                
                // Step 2: Upload
                const isUploaded = await uploadToShreeCloud(videoPath);

                if (isUploaded) {
                    // Step 3: Success hone par URL history.txt mein save karna (taki duplicate na ho)
                    fs.appendFileSync(historyFile, `${video.post_url}\n`);
                    history.push(video.post_url);
                    downloadedCount++;

                    // Step 4: Video file delete karke storage free karna
                    fs.unlinkSync(videoPath);
                    console.log(`🗑️ Deleted local file: ${video.shortcode}.mp4`);
                } else {
                    console.log(`⚠️ Upload fail hua, isliye history mein save nahi kiya. Agli baar try karega.`);
                }

                // 🛑 HUMAN-LIKE SLEEP: Har video ke baad 15s - 30s ka break
                const delayMs = Math.floor(Math.random() * 15000) + 15000;
                console.log(`⏳ Bot is sleeping for ${delayMs / 1000} seconds...`);
                await sleep(delayMs);

            } catch (err) {
                console.error(`❌ Process failed for ${video.shortcode}:`, err.message);
            }
        }
        
        // 🛑 USER BREAK: Ek user ka kaam poora hone ke baad 1 se 2 minute ka break
        if (downloadedCount > 0) {
            const userDelay = Math.floor(Math.random() * 60000) + 60000; 
            console.log(`💤 ${username} process complete. Long rest for ${userDelay / 1000} seconds...`);
            await sleep(userDelay);
        } else {
            console.log(`⏭️ No new videos found for ${username}. Moved to next.`);
        }
    }
    console.log(`\n🎉 All jobs done! Automation Complete.`);
}

startAutomation();
