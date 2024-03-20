document.addEventListener("DOMContentLoaded", function() {
    const demos = [
        { title: "Gandalf Faces the Balrog", imagePath: "static/images/balrog.png", audioPath: "static/audio/demo1.mp3", backingPath: "static/audio/backing.mp3" },
        { title: "Demo 2", imagePath: "static/images/wizard.png", audioPath: "static/audio/demo2.mp3", backingPath: "static/audio/backing.mp3" },
        // Add more demos as needed
    ];

    const demosContainer = document.getElementById("preBuiltDemos");
    const backingAudio = document.getElementById("backingAudio");
    const mainAudio = document.getElementById("mainAudio");
    const volumeSlider = document.getElementById("backingVolume");

    volumeSlider.addEventListener("input", function() {
        backingAudio.volume = this.value;
    });

    // Play the backing track when the main track plays
    mainAudio.addEventListener("play", function() {
        backingAudio.play();
    });

    // Pause the backing track when the main track pauses
    mainAudio.addEventListener("pause", function() {
        backingAudio.pause();
    });

    // Sync backing track with main track when seeking
    mainAudio.addEventListener("seeked", function() {
        backingAudio.currentTime = mainAudio.currentTime;
    });

    demos.forEach(demo => {
        const demoElement = document.createElement("div");
        demoElement.classList.add("demo");
        demoElement.innerHTML = `
            <div class="demo-content">
                <img src="${demo.imagePath}" alt="${demo.title}" />
                <h3>${demo.title}</h3>
            </div>
        `;
        demoElement.addEventListener("click", () => {
            mainAudio.src = demo.audioPath;
            backingAudio.src = demo.backingPath; // Set the backing track source
            if (mainAudio.paused) {
                mainAudio.play();
            } else {
                mainAudio.currentTime = 0; // This will also trigger the 'seeked' event
            }
            // Update Now Playing info
            document.getElementById("nowPlayingImg").src = demo.imagePath;
            document.getElementById("nowPlayingImg").style.display = 'inline'; // Show the image
            document.getElementById("nowPlayingTitle").textContent = demo.title;
        });

        demosContainer.appendChild(demoElement);
    });
    
    
    let mediaRecorder;
    let recordedBlobs;

    const recordBtn = document.getElementById('recordBtn');
    const stopRecordBtn = document.getElementById('stopRecordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordedAudio = document.getElementById('recordedAudio');

    async function initRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                recordedBlobs.push(event.data);
            }
        };
        mediaRecorder.onstop = uploadRecording;
        recordedBlobs = [];
    }

    recordBtn.onclick = () => {
        initRecording().then(() => {
            mediaRecorder.start();
            recordBtn.disabled = true;
            stopRecordBtn.disabled = false;
            recordingStatus.textContent = 'Recording...';
        });
    };

    stopRecordBtn.onclick = () => {
        mediaRecorder.stop();
        recordBtn.disabled = false;
        stopRecordBtn.disabled = true;
        recordingStatus.textContent = 'Not recording';
    };

    function uploadRecording() {
        const blob = new Blob(recordedBlobs, {type: 'audio/mp3'});
        const formData = new FormData();
        formData.append('audioFile', blob, 'userRecording.mp3');
        
        // Simulate processing delay and update UI
        recordingStatus.textContent = 'Processing...';
        fetch('/upload', {method: 'POST', body: formData})
            .then(response => response.json())
            .then(result => {
                console.log(result.message);
                setTimeout(() => {
                    addRecordedDemoToDemosList(blob);
                    recordingStatus.textContent = 'Not recording';
                }, 5000); // Simulate processing time
            })
            .catch(error => {
                console.error('Error:', error);
                recordingStatus.textContent = 'Error during processing.';
            });
    }

    function addRecordedDemoToDemosList(blob) {
        const url = URL.createObjectURL(blob);
        const recordedDemo = {
            title: "Your Recording",
            imagePath: "static/images/user_audio.png", // Placeholder image path
            audioPath: url,
            backingPath: "static/audio/backing.mp3" // Assuming a generic backing track for now
        };
        // Commented out to prevent the recorded audio playback element from appearing
        // recordedAudio.src = url; // Optionally play the recorded audio
        // recordedAudio.hidden = false;
        demos.unshift(recordedDemo); // Add to the start of the demos array
        drawDemos();
    }

    function drawDemos() {
        demosContainer.innerHTML = ''; // Clear existing demos
        demos.forEach(demo => {
            const demoElement = document.createElement("div");
            demoElement.classList.add("demo");
            demoElement.innerHTML = `
                <div class="demo-content">
                    <img src="${demo.imagePath}" alt="${demo.title}" />
                    <h3>${demo.title}</h3>
                </div>
            `;
            demoElement.addEventListener("click", () => {
                mainAudio.src = demo.audioPath;
                backingAudio.src = demo.backingPath;
                if (mainAudio.paused) {
                    mainAudio.play();
                } else {
                    mainAudio.currentTime = 0;
                }
                document.getElementById("nowPlayingImg").src = demo.imagePath;
                document.getElementById("nowPlayingImg").style.display = 'inline';
                document.getElementById("nowPlayingTitle").textContent = demo.title;
            });
            demosContainer.appendChild(demoElement);
        });
    }


    // Ensure to call drawDemos initially to draw the demos for the first time
    drawDemos();
});