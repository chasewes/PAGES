document.addEventListener("DOMContentLoaded", function() {
    const demos = [
        { title: "Harry Potter and Fawkes the Phoenix", imagePath: "static/images/harry_potter.jpg", audioPath: "static/audio/HP_Fox_Audio_Clip_4.mp3", backingPath: "static/audio/HP_Fox_Audio_Clip_4_backing.mp3" },
        { title: "Gandalf Faces the Balrog", imagePath: "static/images/balrog.png", audioPath: "static/audio/balrog_audio.mp3", backingPath: "static/audio/balrog_audio_backing.mp3" },
        { title: "Gandalf Faces the Balrog (FAKE) (PRANK) ", imagePath: "static/images/balrog.png", audioPath: "static/audio/demo1.mp3", backingPath: "static/audio/backing.mp3" },
        { title: "Demo 2", imagePath: "static/images/wizard.png", audioPath: "static/audio/demo2.mp3", backingPath: "static/audio/backing.mp3" },

        // Add more demos as needed
    ];
    // It was confirmed that .wav files do work for audio paths.

    const demosContainer = document.getElementById("preBuiltDemos");
    const backingAudio = document.getElementById("backingAudio");
    const mainAudio = document.getElementById("mainAudio");
    const volumeSlider = document.getElementById("backingVolume");

    
    // Set the backing track volume based on the slider's initial value
    backingAudio.volume = volumeSlider.value; // Add this line

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
                if (result.error) {
                    console.error('Error:', result.error);
                    recordingStatus.textContent = 'Error during processing.';
                } else {
                    console.log('Original file:', result.original);
                    console.log('Processed file:', result.processed);
                    // Here, you can update the UI or do something with the file names
                    recordingStatus.textContent = 'Processing complete.';
                    
                    addNewUserRecordingDemo(result.original, result.processed);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
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
    
    function addNewUserRecordingDemo(original, processed) {
        // Create URL for the original and processed audio files
        const originalAudioPath = `uploads/${original}`;
        const processedAudioPath = `uploads/${processed}`;

        // Add the new demo to the start of the demos array
        demos.unshift({
            title: "User Recording",
            imagePath: "static/images/user_audio.png",
            audioPath: originalAudioPath,
            backingPath: processedAudioPath
        });
        // Redraw the demos list
        drawDemos();
    }


    // Ensure to call drawDemos initially to draw the demos for the first time
    drawDemos();

    const uploadForm = document.getElementById('uploadForm');
    // uploadForm.onsubmit = async function(event) {
    //     event.preventDefault(); // Prevent the default form submission
    //     const formData = new FormData(uploadForm);
        
    //     try {
    //         const response = await fetch('/upload', {
    //             method: 'POST',
    //             body: formData, // FormData object to be sent in the request body
    //         });
    //         const result = await response.json();
            
    //         // Handle the response data from the server
    //         if (response.ok) {
    //             console.log('Upload successful:', result);
    //             // Here, update the UI to reflect the successful upload
    //             // e.g., displaying the processed file or a success message
    //         } else {
    //             console.error('Upload failed:', result.error);
    //             // Update the UI to show the error message
    //         }
    //     } catch (error) {
    //         console.error('Error during fetch:', error);
    //         // Handle network errors or other issues with the fetch call
    //     }
    // };

    function addNewDemoFromUpload(originalFileName, processedFileName) {
        const originalFilePath = `/uploads/${originalFileName}`;
        const processedFilePath = `/uploads/${processedFileName}`;
        // Assuming a naming convention or a static image for uploaded demos
        const demoImage = "static/images/uploaded_audio.png"; // Placeholder image path
    
        const newDemo = {
            title: "Uploaded Audio",
            imagePath: demoImage,
            audioPath: originalFilePath,
            backingPath: processedFilePath
        };
    
        // Add the new demo to the beginning of the demos array
        demos.unshift(newDemo);
    
        // Call a function to redraw the demos on the page
        drawDemos();
    }

    // Modify your upload function to call `addNewDemoFromUpload` upon successful upload
    uploadForm.onsubmit = async function(event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            
            if (response.ok) {
                // Assuming 'original' and 'processed' are the keys in the JSON response
                addNewDemoFromUpload(result.original, result.processed);
                console.log('Upload successful:', result);
            } else {
                console.error('Upload failed:', result.error);
            }
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    };


});