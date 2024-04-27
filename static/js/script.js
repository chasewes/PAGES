document.addEventListener("DOMContentLoaded", function() {
    const demos = [
        { title: "Harry Potter and Fawkes the Phoenix", imagePath: "static/images/harry_potter.jpg", audioPath: "static/audio/HP_Fox_Audio_Clip_4.mp3", backingPath: "static/audio/HP_Fox_Audio_Clip_4_backing.mp3", is_new: false, is_hot: false },
        { title: "The White Knight", imagePath: "static/images/white_knight.jpg", audioPath: "static/audio/White_Knights_Aleesha_Bake_1.mp3", backingPath: "static/audio/White_Knights_Aleesha_Bake_1_backing.mp3", is_new: false, is_hot: false },
        // { title: "Taco Bell Ad", imagePath: "static/images/Taco_Bell.jpg", audioPath: "static/audio/Taco_Bell.mp3", backingPath: "static/audio/Taco_Bell_backing.mp3" },
        { title: "Taco Bell", imagePath: "static/images/Taco_Bell.jpg", audioPath: "static/audio/Taco_Bell_Vocals.mp3", backingPath: "static/audio/Taco_Bell_Vocals_backing.mp3", is_new: false, is_hot: true },
        { title: "Dwarf", imagePath: "static/images/dwarf.png", audioPath: "static/audio/Steven-Varnum-WINNER-MALE.mp3", backingPath: "static/audio/Steven-Varnum-WINNER-MALE_backing.mp3", is_new: false, is_hot: true },
        { title: "Paul Bear", imagePath: "static/images/paul_bear.png", audioPath: "static/audio/Paul_Bear.mp3", backingPath: "static/audio/Paul_Bear_backing.mp3", is_new: false, is_hot: false },
        { title: "Gandalf Faces the Balrog", imagePath: "static/images/balrog.png", audioPath: "static/audio/balrog_audio.mp3", backingPath: "static/audio/balrog_audio_backing.mp3", is_new: false, is_hot: false },
        { title: "Gandalf Faces the Balrog 2.0", imagePath: "static/images/balrog.png", audioPath: "static/audio/balrog_audio.mp3", backingPath: "static/audio/extras/balrog_alt_backing.mp3", is_new: true, is_hot: true },
        { title: "Sneaky Russian Problem", imagePath: "static/images/extras/cia.png", audioPath: "static/audio/extras/cia.mp3", backingPath: "static/audio/extras/cia_backing.mp3", is_new: true, is_hot: false },
        { title: "Australian Bench Warmer", imagePath: "static/images/extras/emily_lawrence_australian_romcom.png", audioPath: "static/audio/extras/emily_lawrence_australian_romcom.mp3", backingPath: "static/audio/extras/emily_lawrence_australian_romcom_backing.mp3", is_new: true, is_hot: false },
        { title: "Water", imagePath: "static/images/extras/water.png", audioPath: "static/audio/extras/water.mp3", backingPath: "static/audio/extras/water_backing.mp3", is_new: true, is_hot: false },
        { title: "Rochambeau", imagePath: "static/images/extras/rochambeau.png", audioPath: "static/audio/extras/rochambeau.mp3", backingPath: "static/audio/extras/rochambeau_backing.mp3", is_new: true, is_hot: false },
        { title: "Meeting the Native Americans", imagePath: "static/images/extras/emily_lawrence_nonfiction.png", audioPath: "static/audio/extras/emily_lawrence_nonfiction.mp3", backingPath: "static/audio/extras/emily_lawrence_nonfiction_backing.mp3", is_new: true, is_hot: false },
        { title: "Ventura Faces the Balrog 1.0", imagePath: "static/images/ventura.png", audioPath: "static/audio/ventura.mp3", backingPath: "static/audio/ventura_backing.mp3", is_new: true, is_hot: true },
        { title: "Ventura Faces the Balrog 2.0", imagePath: "static/images/ventura.png", audioPath: "static/audio/ventura.mp3", backingPath: "static/audio/extras/balrog_alt_backing.mp3", is_new: true, is_hot: true },


        // { title: "", imagePath: "static/images/extras/.png", audioPath: "static/audio/extras/.mp3", backingPath: "static/audio/extras/_backing.mp3", is_new: true, is_hot: false },
        


        // { title: "Gandalf Faces the Balrog (FAKE) (PRANK) ", imagePath: "static/images/balrog.png", audioPath: "static/audio/demo1.mp3", backingPath: "static/audio/backing.mp3" },
        // { title: "Demo 2", imagePath: "static/images/wizard.png", audioPath: "static/audio/demo2.mp3", backingPath: "static/audio/backing.mp3" },

        // Add more demos as needed
    ];
    // It was confirmed that .wav files do work for audio paths.

    const demosContainer = document.getElementById("preBuiltDemos");
    const backingAudio = document.getElementById("backingAudio");
    const mainAudio = document.getElementById("mainAudio");
    const volumeSlider = document.getElementById("backingVolume");

    // const recentContainer = document.getElementById("recentUploads");
    
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

        // Create prefix based on the is_new and is_hot properties
        // let titlePrefix = '';
        // if (demo.is_hot) {
        //     titlePrefix += '🔥';
        // }
        // if (demo.is_new) {
        //     titlePrefix += '🆕';
        // }

        // Initialize the title prefix
        let titlePrefix = '';

        // Check for 'is_hot' and 'is_new' properties before adding icons
        if (demo.is_hot === true) {
            titlePrefix += '🔥';
        }
        if (demo.is_new === true) {
            titlePrefix += '🆕';
        }

        let new_title = titlePrefix + demo.title;

        demoElement.innerHTML = `
            <div class="demo-content">
                <img src="${demo.imagePath}" alt="${demo.title}" />
                <h3>${new_title}</h3>
            </div>
        `;
        // <h3>${demo.title}</h3>
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
            // document.getElementById("nowPlayingTitle").textContent = demo.title;
            document.getElementById("nowPlayingTitle").textContent = new_title;

        });

        demosContainer.appendChild(demoElement);
    });


    function fetchAndDisplayRecentUploads() {
        fetch('/api/recent-uploads')
            .then(response => response.json())
            .then(demos => {
                const recentUploadsContainer = document.getElementById("recentUploads");
                recentUploadsContainer.innerHTML = ''; // Clear existing content
    
                demos.forEach(demo => {
                    const demoElement = document.createElement("div");
                    demoElement.classList.add("demo");
                    demoElement.innerHTML = `
                        <div class="demo-content">
                            <img src="static/images/user_audio.png" alt="${demo.main}" />
                            <h3>${demo.main.split('.')[0]}</h3> <!-- Displaying basename as title -->
                        </div>
                    `;
                    demoElement.addEventListener("click", () => {
                        // Assuming global variables for mainAudio and backingAudio
                        mainAudio.src = `uploads/${demo.main}`;
                        backingAudio.src = `uploads/${demo.backing}`;
                        document.getElementById("nowPlayingImg").src = "static/images/user_audio.png";
                        document.getElementById("nowPlayingImg").style.display = 'inline';
                        document.getElementById("nowPlayingTitle").textContent = demo.main.split('.')[0]; // Set title to basename
                        if (mainAudio.paused) {
                            mainAudio.play();
                        } else {
                            mainAudio.currentTime = 0; // This will also trigger the 'seeked' event
                        }
                    });
    
                    recentUploadsContainer.appendChild(demoElement);
                });
            })
            .catch(error => console.error('Error fetching recent uploads:', error));
    }


    const toggleBtn = document.getElementById("toggleRecentUploadsBtn");
    const recentUploadsDiv = document.getElementById("recentUploads");

    toggleBtn.addEventListener("click", function() {
        if (recentUploadsDiv.style.display === "none") {
            recentUploadsDiv.style.display = "block"; // Show the section
            toggleBtn.textContent = "Hide"; // Optionally change the button text to "Hide"
        } else {
            recentUploadsDiv.style.display = "none"; // Hide the section
            toggleBtn.textContent = "Show"; // Optionally change the button text to "Show"
        }
    });

    // Ensure to call fetchAndDisplayRecentUploads initially to populate the section
    fetchAndDisplayRecentUploads();

        
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
            backingPath: "static/audio/backing.mp3", // Assuming a generic backing track for now
            is_new: true, // Mark the demo as new
            is_hot: false // Mark the demo as not hot
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

            // Initialize the title prefix
            let titlePrefix = '';

            // Check for 'is_hot' and 'is_new' properties before adding icons
            if (demo.is_hot === true) {
                titlePrefix += '🔥';
            }
            if (demo.is_new === true) {
                titlePrefix += '🆕';
            }
            let new_title = titlePrefix + demo.title;

            demoElement.innerHTML = `
                <div class="demo-content">
                    <img src="${demo.imagePath}" alt="${demo.title}" />
                    <h3>${new_title}</h3>
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
                document.getElementById("nowPlayingTitle").textContent = new_title;
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
            backingPath: processedAudioPath,
            is_new: true,
            is_hot: false
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
        const demoImage = "static/images/user_audio.png"; // Placeholder image path
    
        const newDemo = {
            title: "Uploaded Audio",
            imagePath: demoImage,
            audioPath: originalFilePath,
            backingPath: processedFilePath,
            is_new: true, // Mark the demo as new
            is_hot: false // Mark the demo as not hot
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

    

    document.querySelectorAll('.demo').forEach(demo => {
        const img = demo.querySelector('img'); // Ensure you're targeting the image within the demo
        demo.addEventListener('mousemove', function(e) {
            const {width, height, left, top} = this.getBoundingClientRect();
            const x = e.clientX - left;
            const y = e.clientY - top;
            const deltaX = (x - width / 2) / (width / 2); // Normalize the coordinates
            const deltaY = (y - height / 2) / (height / 2); // Normalize the coordinates
    
            // Increase the multiplier for horizontal rotation to make it more extreme
            const horizontalRotationDegree = 30; // Increase for more extreme horizontal rotation
            const verticalRotationDegree = 20;  // Keep the vertical rotation more subtle
    
            img.style.transform = `rotateY(${deltaX * horizontalRotationDegree}deg) rotateX(${deltaY * verticalRotationDegree * -1}deg)`;
        });
    
        demo.addEventListener('mouseleave', function() {
            // Reset the image rotation on mouse leave
            img.style.transform = 'rotateX(0) rotateY(0)';
        });
    });

});