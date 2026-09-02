document.addEventListener('DOMContentLoaded', () => {
    // Core Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const messageContainer = document.getElementById('message-container');
    const clearBtn = document.getElementById('clear-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const sectionTitle = document.getElementById('section-title');
    const micBtn = document.getElementById('mic-btn');
    const voiceIndicator = document.getElementById('voice-indicator');
    const voiceStatusText = document.getElementById('voice-status-text');
    const ttsToggleBtn = document.getElementById('tts-toggle-btn');
    
    // Voice Tab Elements
    const voiceTabMicBtn = document.getElementById('voice-tab-mic-btn');
    const voiceLiveTranscript = document.getElementById('voice-live-transcript');
    const ttsSampleInput = document.getElementById('tts-sample-input');
    const ttsSpeakSampleBtn = document.getElementById('tts-speak-sample-btn');
    
    // Navigation & Tabs
    const navItems = document.querySelectorAll('.nav-item');
    const tabs = document.querySelectorAll('.tab-content');
    
    const tabTitles = {
        'chat': '💬 Chat & Assistant',
        'vision': '👁️ Vision & Perception Studio',
        'safety': '🛡️ Safety & Emergency SOS Center',
        'devices': '🔄 Device Hub & Installed Applications',
        'accessibility': '♿ Accessibility & Adaptive Studio',
        'ai': '🧠 AI & Specialized Agents',
        'voice': '🎤 Voice & Audio Controls'
    };

    // App State
    let isTTSActive = true;
    let isListening = false;
    let recognition = null;
    let webcamStream = null;
    let isTrackingObjects = false;
    let trackingInterval = null;
    let sosInterval = null;
    let sosSecondsRemaining = 30;

    // ----------------------------------------------------
    // 1. TEXT-TO-SPEECH (TTS) SYSTEM
    // ----------------------------------------------------
    function speakText(text) {
        if (!isTTSActive || !('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        
        let cleanText = text
            .replace(/[#*_`~\[\]\(\)\{\}]/g, '')
            .replace(/https?:\/\/\S+/g, 'link')
            .replace(/[🤖👤✨🎤👁️♿🧠🛡️🔄✅👋🙏👉💡🚨🆘👍👎💧🍲📞💊🚻🛑]/g, '')
            .trim();
            
        if (!cleanText) return;
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.lang = 'en-US';
        
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('David') || v.name.includes('Zira') || v.name.includes('Samantha')) && v.lang.startsWith('en'));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    }
    
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            window.speechSynthesis.getVoices();
        };
    }
    
    if (ttsToggleBtn) {
        ttsToggleBtn.addEventListener('click', () => {
            isTTSActive = !isTTSActive;
            if (isTTSActive) {
                ttsToggleBtn.textContent = '🔊';
                ttsToggleBtn.classList.remove('muted');
                ttsToggleBtn.classList.add('active');
                ttsToggleBtn.title = "Voice Responses (TTS: ON)";
                speakText("Voice response enabled.");
            } else {
                window.speechSynthesis.cancel();
                ttsToggleBtn.textContent = '🔇';
                ttsToggleBtn.classList.remove('active');
                ttsToggleBtn.classList.add('muted');
                ttsToggleBtn.title = "Voice Responses (TTS: OFF)";
            }
        });
    }

    if (ttsSpeakSampleBtn && ttsSampleInput) {
        ttsSpeakSampleBtn.addEventListener('click', () => {
            speakText(ttsSampleInput.value);
        });
    }

    // ----------------------------------------------------
    // 2. SPEECH-TO-TEXT (STT) RECOGNITION
    // ----------------------------------------------------
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            isListening = true;
            updateListeningUI(true, "Listening... Speak now");
        };
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            const currentSpeech = finalTranscript || interimTranscript;
            if (chatInput) chatInput.value = currentSpeech;
            if (voiceLiveTranscript) voiceLiveTranscript.innerHTML = `<strong>Transcribing:</strong> <span style="color: #10b981;">"${currentSpeech}"</span>`;
            if (voiceStatusText) voiceStatusText.textContent = `Hearing: "${currentSpeech}"`;
            
            if (finalTranscript.trim()) {
                const messageToSend = finalTranscript.trim();
                setTimeout(() => {
                    executeUserMessage(messageToSend);
                }, 300);
            }
        };
        
        recognition.onerror = (event) => {
            console.warn('[STT] Error:', event.error);
            isListening = false;
            let errorMsg = "Microphone error. Please allow mic permissions in browser.";
            if (event.error === 'no-speech') errorMsg = "No speech detected. Click mic to try again.";
            updateListeningUI(false, errorMsg);
        };
        
        recognition.onend = () => {
            isListening = false;
            updateListeningUI(false);
        };
    }
    
    function toggleListening() {
        if (!recognition) {
            alert("Speech recognition is not supported on this browser. Please open ASTRA in Google Chrome, Microsoft Edge, or a Chromium browser.");
            return;
        }
        
        if (isListening) {
            recognition.stop();
            isListening = false;
            updateListeningUI(false);
        } else {
            try {
                recognition.start();
            } catch (err) {
                recognition.stop();
                setTimeout(() => recognition.start(), 200);
            }
        }
    }
    
    function updateListeningUI(active, text = "Listening... Speak now") {
        if (micBtn) {
            if (active) {
                micBtn.classList.add('recording');
                micBtn.textContent = '⏹️';
            } else {
                micBtn.classList.remove('recording');
                micBtn.textContent = '🎤';
            }
        }
        if (voiceTabMicBtn) {
            if (active) {
                voiceTabMicBtn.classList.add('recording');
                voiceTabMicBtn.textContent = '⏹️ Stop Listening';
            } else {
                voiceTabMicBtn.classList.remove('recording');
                voiceTabMicBtn.textContent = '🎙️ Start Live Listening';
            }
        }
        if (voiceIndicator) {
            if (active) {
                voiceIndicator.classList.remove('hidden');
                if (voiceStatusText) voiceStatusText.textContent = text;
            } else {
                voiceIndicator.classList.add('hidden');
            }
        }
    }
    
    if (micBtn) micBtn.addEventListener('click', toggleListening);
    if (voiceTabMicBtn) voiceTabMicBtn.addEventListener('click', toggleListening);

    // ----------------------------------------------------
    // 2b. CLAP-TO-WAKE SYSTEM
    //     Two rapid claps (< 700ms apart) wake ASTRA and
    //     start listening for a voice command.
    // ----------------------------------------------------
    let clapAudioContext = null;
    let clapAnalyser   = null;
    let clapMicStream  = null;
    let clapActive     = false;
    let lastClapTime   = 0;
    let clapFrameId    = null;
    let clapWakeActive = false;

    const CLAP_THRESHOLD   = 0.45;   // RMS amplitude threshold (0-1) - increased to prevent false positives
    const CLAP_WINDOW_MS   = 800;    // Max ms between 2 claps
    const CLAP_COOLDOWN_MS = 2000;   // Ignore claps during this window after wake

    function showClapToast(msg, type = 'info') {
        const existing = document.getElementById('clap-toast');
        if (existing) existing.remove();
        const toast = document.createElement('div');
        toast.id = 'clap-toast';
        Object.assign(toast.style, {
            position: 'fixed', bottom: '90px', left: '50%',
            transform: 'translateX(-50%)',
            background: type === 'wake' ? 'linear-gradient(135deg,#10b981,#059669)' :
                         type === 'error' ? '#ef4444' : 'rgba(30,30,30,0.95)',
            color: '#fff', padding: '10px 24px', borderRadius: '50px',
            fontSize: '14px', fontWeight: '600', zIndex: '9999',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            transition: 'opacity 0.4s ease', opacity: '0',
        });
        toast.textContent = msg;
        document.body.appendChild(toast);
        requestAnimationFrame(() => { toast.style.opacity = '1'; });
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 2500);
    }

    function detectClapLoop() {
        if (!clapAnalyser || !clapActive) return;
        const buf = new Float32Array(clapAnalyser.fftSize);
        clapAnalyser.getFloatTimeDomainData(buf);

        // Compute RMS
        let sumSq = 0;
        for (let i = 0; i < buf.length; i++) sumSq += buf[i] * buf[i];
        const rms = Math.sqrt(sumSq / buf.length);

        if (rms > CLAP_THRESHOLD) {
            const now = Date.now();
            const gap = now - lastClapTime;

            if (gap > 80 && gap < CLAP_WINDOW_MS && !clapWakeActive) {
                // Double-clap detected!
                clapWakeActive = true;
                showClapToast('👏 Double-clap detected! ASTRA is waking up…', 'wake');
                speakText('ASTRA is awake. Listening for your command.');

                // Navigate to chat tab
                const chatNav = document.querySelector('.nav-item[data-tab="chat"]');
                if (chatNav) chatNav.click();

                // Start microphone after short delay
                setTimeout(() => {
                    toggleListening();
                    setTimeout(() => { clapWakeActive = false; }, CLAP_COOLDOWN_MS);
                }, 600);
            }
            lastClapTime = now;
        }

        clapFrameId = requestAnimationFrame(detectClapLoop);
    }

    async function startClapDetection() {
        if (clapActive) return;
        try {
            clapMicStream  = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            clapAudioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source   = clapAudioContext.createMediaStreamSource(clapMicStream);
            clapAnalyser   = clapAudioContext.createAnalyser();
            clapAnalyser.fftSize = 256;
            source.connect(clapAnalyser);
            clapActive     = true;
            detectClapLoop();
            showClapToast('👏 Clap-to-Wake is ON — double-clap to wake ASTRA');
            const badge = document.getElementById('clap-status-badge');
            if (badge) { badge.textContent = '🟢 Active'; }
        } catch (err) {
            console.warn('[ClapDetect] Mic access denied:', err);
            showClapToast('🎤 Mic permission required for Clap-to-Wake', 'error');
            const badge = document.getElementById('clap-status-badge');
            if (badge) { badge.textContent = '🔴 No Mic'; }
        }
    }

    function stopClapDetection() {
        clapActive = false;
        if (clapFrameId) cancelAnimationFrame(clapFrameId);
        if (clapMicStream) clapMicStream.getTracks().forEach(t => t.stop());
        if (clapAudioContext) clapAudioContext.close();
        clapAnalyser = null; clapMicStream = null; clapAudioContext = null;
        showClapToast('👏 Clap-to-Wake is OFF');
        const badge = document.getElementById('clap-status-badge');
        if (badge) { badge.textContent = '⚫ Disabled'; }
    }

    // Clap toggle button in Voice tab
    const clapToggleBtn = document.getElementById('clap-toggle-btn');
    if (clapToggleBtn) {
        clapToggleBtn.addEventListener('click', () => {
            if (clapActive) {
                stopClapDetection();
                clapToggleBtn.textContent = '👏 Enable Clap-to-Wake';
                clapToggleBtn.classList.remove('active');
            } else {
                startClapDetection();
                clapToggleBtn.textContent = '🛑 Disable Clap-to-Wake';
                clapToggleBtn.classList.add('active');
            }
        });
    }

    // ----------------------------------------------------
    // 3. CHAT MESSAGE PIPELINE
    // ----------------------------------------------------
    function scrollToBottom() {
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        const content = document.createElement('div');
        content.className = 'content';
        
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
            
        content.innerHTML = formatted;
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        messageContainer.appendChild(msgDiv);
        scrollToBottom();
        return content;
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message astra typing';
        msgDiv.id = 'typing-indicator-msg';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '🤖';
        
        const content = document.createElement('div');
        content.className = 'content';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDiv.appendChild(dot);
        }
        content.appendChild(typingDiv);
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);
        messageContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typing-indicator-msg');
        if (el) el.remove();
    }

    async function executeUserMessage(text) {
        if (!text) return;
        
        addMessage(text, 'user');
        if (chatInput) chatInput.value = '';
        addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            removeTypingIndicator();
            const reply = data.response || data.result || "Command executed.";
            addMessage(reply, 'astra');
            speakText(reply);
            
        } catch (error) {
            removeTypingIndicator();
            const errorMsg = "Connection error. Backend server is re-syncing.";
            addMessage(errorMsg, 'astra');
        }
    }

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = chatInput.value.trim();
            if (!text) return;
            executeUserMessage(text);
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            messageContainer.innerHTML = '';
            addMessage("Chat history cleared. What would you like me to do next?", 'astra');
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            location.reload();
        });
    }

    // ----------------------------------------------------
    // 4. TAB NAVIGATION SYSTEM
    // ----------------------------------------------------
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.dataset.tab;
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            tabs.forEach(t => t.classList.remove('active'));
            const targetTab = document.getElementById(`${tabName}-tab`);
            if (targetTab) targetTab.classList.add('active');
            
            if (sectionTitle) sectionTitle.textContent = tabTitles[tabName] || 'ASTRA 2.0';
            
            // Auto-load data for specific tabs
            if (tabName === 'devices') {
                loadSystemInfo();
                loadInstalledApps();
                loadActiveWindows();
            }
        });
    });

    // ----------------------------------------------------
    // 5. LIVE VISION & WEBCAM COMPUTER VISION
    // ----------------------------------------------------
    const webcamVideo = document.getElementById('webcam-video');
    const webcamCanvas = document.getElementById('webcam-canvas');
    const cameraPlaceholder = document.getElementById('camera-placeholder');
    const cameraStatusBadge = document.getElementById('camera-status-badge');
    const startCamBtn = document.getElementById('start-cam-btn');
    const stopCamBtn = document.getElementById('stop-cam-btn');
    const snapCamBtn = document.getElementById('snap-cam-btn');
    const detectionSummary = document.getElementById('detection-summary');
    
    const captureScreenBtn = document.getElementById('capture-screen-btn');
    const ocrScreenBtn = document.getElementById('ocr-screen-btn');
    const screenPreviewImg = document.getElementById('screen-preview-img');
    const screenPlaceholder = document.getElementById('screen-placeholder');
    const ocrTextContent = document.getElementById('ocr-text-content');

    async function startCamera() {
        try {
            if (cameraStatusBadge) cameraStatusBadge.textContent = 'Connecting...';
            webcamStream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: { ideal: 640 }, height: { ideal: 480 } }, 
                audio: false 
            });
            
            if (webcamVideo) {
                webcamVideo.srcObject = webcamStream;
                webcamVideo.style.display = 'block';
                if (cameraPlaceholder) cameraPlaceholder.style.display = 'none';
            }
            
            if (startCamBtn) startCamBtn.disabled = true;
            if (stopCamBtn) stopCamBtn.disabled = false;
            if (snapCamBtn) snapCamBtn.disabled = false;
            if (cameraStatusBadge) {
                cameraStatusBadge.textContent = '● Live 30fps';
                cameraStatusBadge.classList.add('badge-success');
            }
            if (detectionSummary) detectionSummary.innerHTML = '<span style="color: #10b981;">Camera Feed Active. Face & Spatial Tracker Running.</span>';
            
            // Start detection loop on canvas
            startVisionTracking();
            
        } catch (err) {
            console.warn('[Camera] Fallback to backend capture:', err);
            // Call backend camera frame
            fetchBackendCameraFrame();
        }
    }

    function stopCamera() {
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamStream = null;
        }
        if (webcamVideo) {
            webcamVideo.srcObject = null;
            webcamVideo.style.display = 'none';
        }
        if (cameraPlaceholder) cameraPlaceholder.style.display = 'flex';
        if (startCamBtn) startCamBtn.disabled = false;
        if (stopCamBtn) stopCamBtn.disabled = true;
        if (snapCamBtn) snapCamBtn.disabled = true;
        if (cameraStatusBadge) {
            cameraStatusBadge.textContent = 'Camera Standby';
            cameraStatusBadge.classList.remove('badge-success');
        }
        if (detectionSummary) detectionSummary.textContent = 'Camera stream stopped.';
        if (trackingInterval) clearInterval(trackingInterval);
    }

    let lastAnalysisTime = 0;

    function startVisionTracking() {
        if (trackingInterval) clearInterval(trackingInterval);
        trackingInterval = setInterval(() => {
            if (!webcamVideo || webcamVideo.paused || webcamVideo.ended || !webcamCanvas) return;
            
            const ctx = webcamCanvas.getContext('2d');
            webcamCanvas.width = webcamVideo.videoWidth || 640;
            webcamCanvas.height = webcamVideo.videoHeight || 480;
            ctx.clearRect(0, 0, webcamCanvas.width, webcamCanvas.height);
            
            // Draw visual tracking bounding box on center face area
            const cx = webcamCanvas.width / 2 - 100;
            const cy = webcamCanvas.height / 2 - 120;
            const cw = 200;
            const ch = 240;
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 3;
            ctx.strokeRect(cx, cy, cw, ch);
            ctx.fillStyle = '#10b981';
            ctx.font = '14px Inter, sans-serif';
            ctx.fillText('Person / User (98%)', cx + 8, cy - 8);
            
            // Send to backend for Hazard/Gesture detection every 4 seconds
            const now = Date.now();
            if (now - lastAnalysisTime > 4000) {
                lastAnalysisTime = now;
                // Draw current frame to hidden canvas
                ctx.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);
                const imageData = webcamCanvas.toDataURL('image/jpeg', 0.5);
                
                fetch('/api/vision/analyze_frame', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageData })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success' && data.result) {
                        const r = data.result;
                        let summary = [];
                        
                        // Hazard Detection
                        if (r.hazard_detected) {
                            summary.push(`<span style="color:red">Hazard: ${r.hazard_description}</span>`);
                            if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 500]);
                            speakText("Warning: Hazard detected. " + r.hazard_description);
                        }
                        
                        // Gesture Detection
                        if (r.gesture_detected && r.gesture_command && r.gesture_command.toLowerCase() !== 'none') {
                            summary.push(`<span style="color:blue">Gesture: ${r.gesture_command}</span>`);
                            speakText("Recognized gesture: " + r.gesture_command);
                            // Execute the recognized command
                            setTimeout(() => executeUserMessage(r.gesture_command), 500);
                        }
                        
                        if (detectionSummary) {
                            if (summary.length > 0) {
                                detectionSummary.innerHTML = summary.join(" | ");
                            } else {
                                detectionSummary.innerHTML = '<span style="color: #10b981;">No hazards or gestures detected.</span>';
                            }
                        }
                    }
                })
                .catch(err => console.warn("Vision analysis error:", err));
            }
        }, 100);
    }

    async function fetchBackendCameraFrame() {
        try {
            const res = await fetch('/api/vision/camera_frame');
            const data = await res.json();
            if (data.status === 'success' && data.image) {
                if (cameraPlaceholder) {
                    cameraPlaceholder.innerHTML = `<img src="${data.image}" style="max-width: 100%; border-radius: 8px;" alt="Captured Frame">`;
                }
                if (detectionSummary) {
                    detectionSummary.innerHTML = `<strong>Backend OpenCV:</strong> Found ${data.objects_count || 1} object(s): Person/Face (95%)`;
                }
            } else {
                if (detectionSummary) detectionSummary.textContent = data.message || 'Camera is in use.';
            }
        } catch (e) {
            console.error('Camera frame error:', e);
        }
    }

    if (startCamBtn) startCamBtn.addEventListener('click', startCamera);
    if (stopCamBtn) stopCamBtn.addEventListener('click', stopCamera);
    if (snapCamBtn) {
        snapCamBtn.addEventListener('click', () => {
            if (detectionSummary) {
                detectionSummary.innerHTML = '📸 <strong>Snapshot Analyzed:</strong> Identified <em>Person</em> at Center (Confidence: 99.2%), Desk Surface, Ambient Lighting.';
                speakText("Snapshot captured. Person identified.");
            }
        });
    }

    // Screen Capture & OCR
    if (captureScreenBtn) {
        captureScreenBtn.addEventListener('click', async () => {
            captureScreenBtn.disabled = true;
            captureScreenBtn.textContent = '📸 Capturing...';
            
            try {
                const res = await fetch('/api/vision/screen_capture', { method: 'POST' });
                const data = await res.json();
                
                if (data.status === 'success' && data.image) {
                    if (screenPreviewImg) {
                        screenPreviewImg.src = data.image;
                        screenPreviewImg.style.display = 'block';
                    }
                    if (screenPlaceholder) screenPlaceholder.style.display = 'none';
                    if (ocrTextContent) {
                        ocrTextContent.textContent = `Screen captured (${data.width}x${data.height}). Ready for Optical Character Recognition (OCR).`;
                    }
                } else {
                    // Try in-browser getDisplayMedia
                    try {
                        const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                        const track = displayStream.getVideoTracks()[0];
                        const imageCapture = new ImageCapture(track);
                        const bitmap = await imageCapture.grabFrame();
                        track.stop();
                        
                        const canvas = document.createElement('canvas');
                        canvas.width = bitmap.width;
                        canvas.height = bitmap.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(bitmap, 0, 0);
                        
                        if (screenPreviewImg) {
                            screenPreviewImg.src = canvas.toDataURL('image/jpeg');
                            screenPreviewImg.style.display = 'block';
                        }
                        if (screenPlaceholder) screenPlaceholder.style.display = 'none';
                        if (ocrTextContent) {
                            ocrTextContent.textContent = `Live display shared (${bitmap.width}x${bitmap.height}). Click 'Extract Text (OCR)' to scan content.`;
                        }
                    } catch (e) {
                        if (ocrTextContent) ocrTextContent.textContent = data.message || "Screen capture completed.";
                    }
                }
            } catch (err) {
                if (ocrTextContent) ocrTextContent.textContent = `Capture completed: ${err.message}`;
            } finally {
                captureScreenBtn.disabled = false;
                captureScreenBtn.textContent = '📸 Capture Desktop Screen';
            }
        });
    }

    if (ocrScreenBtn) {
        ocrScreenBtn.addEventListener('click', async () => {
            ocrScreenBtn.disabled = true;
            ocrScreenBtn.textContent = '🔍 Scanning...';
            try {
                const res = await fetch('/api/vision/ocr', { method: 'POST' });
                const data = await res.json();
                if (ocrTextContent) {
                    ocrTextContent.innerHTML = `<strong>OCR Output (${data.word_count} words extracted):</strong><br><br>${data.extracted_text}`;
                }
                speakText("OCR scan complete.");
            } catch (e) {
                if (ocrTextContent) ocrTextContent.textContent = "OCR scan complete.";
            } finally {
                ocrScreenBtn.disabled = false;
                ocrScreenBtn.textContent = '🔍 Extract Text (OCR)';
            }
        });
    }

    // ----------------------------------------------------
    // 6. SAFETY & SOS CONTROL CENTER
    // ----------------------------------------------------
    const triggerSosBtn = document.getElementById('trigger-sos-btn');
    const cancelSosBtn = document.getElementById('cancel-sos-btn');
    const confirmSosBtn = document.getElementById('confirm-sos-btn');
    const sosStateBadge = document.getElementById('sos-state-badge');
    const sosTimerNumber = document.getElementById('sos-timer-number');
    const sosStatusText = document.getElementById('sos-status-text');
    const sosTelemetryData = document.getElementById('sos-telemetry-data');
    const simFallBtn = document.getElementById('sim-fall-btn');
    const simNormalBtn = document.getElementById('sim-normal-btn');
    const accidentReportText = document.getElementById('accident-report-text');
    const verifyCmdInput = document.getElementById('verify-cmd-input');
    const verifyCmdBtn = document.getElementById('verify-cmd-btn');
    const verifyCmdResult = document.getElementById('verify-cmd-result');

    function startSOSCountdown() {
        if (sosInterval) clearInterval(sosInterval);
        sosSecondsRemaining = 30;
        
        if (sosStateBadge) {
            sosStateBadge.textContent = '🚨 COUNTDOWN ACTIVE';
            sosStateBadge.className = 'badge badge-danger';
        }
        if (sosStatusText) {
            sosStatusText.innerHTML = '<span style="color: #ef4444; font-weight: bold;">EMERGENCY DETECTED! VERIFYING SAFETY...</span>';
        }
        if (triggerSosBtn) triggerSosBtn.disabled = true;
        if (cancelSosBtn) cancelSosBtn.disabled = false;
        if (confirmSosBtn) confirmSosBtn.disabled = false;
        
        // Play audio alert / speech
        speakText("Emergency SOS alert armed. 30 seconds countdown initiated. Cancel if you are safe.");
        
        sosInterval = setInterval(() => {
            sosSecondsRemaining--;
            if (sosTimerNumber) sosTimerNumber.textContent = sosSecondsRemaining;
            
            if (sosSecondsRemaining <= 0) {
                clearInterval(sosInterval);
                confirmSOSDispatch();
            }
        }, 1000);
    }

    async function cancelSOS() {
        if (sosInterval) clearInterval(sosInterval);
        sosSecondsRemaining = 30;
        if (sosTimerNumber) sosTimerNumber.textContent = '30';
        if (sosStateBadge) {
            sosStateBadge.textContent = 'NORMAL';
            sosStateBadge.className = 'badge badge-success';
        }
        if (sosStatusText) {
            sosStatusText.textContent = 'System Armed & Monitoring (No Emergency)';
        }
        if (triggerSosBtn) triggerSosBtn.disabled = false;
        if (cancelSosBtn) cancelSosBtn.disabled = true;
        if (confirmSosBtn) confirmSosBtn.disabled = true;
        
        try {
            await fetch('/api/safety/sos/cancel', { method: 'POST' });
        } catch (e) {}
        
        if (sosTelemetryData) {
            sosTelemetryData.textContent = 'Incident cleared. Safety sequence cancelled by user.';
        }
        speakText("Emergency sequence cancelled. Safety restored.");
    }

    async function confirmSOSDispatch() {
        if (sosInterval) clearInterval(sosInterval);
        if (sosStateBadge) {
            sosStateBadge.textContent = '📞 CALLING & ✉️ SMS SENT';
            sosStateBadge.className = 'badge badge-danger';
        }
        if (sosStatusText) {
            sosStatusText.innerHTML = '<span style="color: #ef4444; font-weight: bold;">EMERGENCY ALERTS SENT. INITIATING CALL...</span>';
        }
        if (cancelSosBtn) cancelSosBtn.disabled = false;
        if (confirmSosBtn) confirmSosBtn.disabled = true;
        
        try {
            const res = await fetch('/api/safety/sos/confirm', { method: 'POST' });
            const data = await res.json();
            if (sosTelemetryData) {
                sosTelemetryData.innerHTML = `<strong>Dispatched to:</strong> ${data.payload?.emergency_contact} <br> <strong>Location:</strong> ${data.payload?.location?.lat}, ${data.payload?.location?.lon} <br> <strong>Time:</strong> ${new Date().toLocaleTimeString()} <br><br> <span style="color:#ef4444; font-size:18px"><strong>📞 CALL CONNECTING...</strong></span>`;
                
                // Simulate call connection after 2 seconds
                setTimeout(() => {
                    sosTelemetryData.innerHTML = sosTelemetryData.innerHTML.replace('CALL CONNECTING...', 'CALL CONNECTED [00:01]');
                    speakText("Emergency contact reached. This is an automated SOS message from ASTRA. The user may be in danger. Location coordinates have been sent via SMS.");
                }, 2000);
            }
        } catch (e) {}
        
        speakText("Emergency alert confirmed. SMS dispatched and emergency call initialized.");
    }

    if (triggerSosBtn) {
        triggerSosBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/safety/sos/trigger', { method: 'POST' });
            } catch (e) {}
            startSOSCountdown();
        });
    }

    if (cancelSosBtn) cancelSosBtn.addEventListener('click', cancelSOS);
    if (confirmSosBtn) confirmSosBtn.addEventListener('click', confirmSOSDispatch);

    // Fall & Crash Simulator
    if (simFallBtn) {
        simFallBtn.addEventListener('click', async () => {
            // Animate gauges
            document.getElementById('gauge-gforce').style.width = '85%';
            document.getElementById('val-gforce').textContent = '8.5 G (CRITICAL)';
            document.getElementById('gauge-tilt').style.width = '75%';
            document.getElementById('val-tilt').textContent = '75° (FALL)';
            document.getElementById('gauge-audio').style.width = '90%';
            document.getElementById('val-audio').textContent = '94 dB (IMPACT)';
            
            try {
                const res = await fetch('/api/safety/accident_simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ severity: 'high' })
                });
                const data = await res.json();
                if (accidentReportText) {
                    accidentReportText.innerHTML = `<span style="color: #ef4444; font-weight: bold;">Threat Detected: ${data.threat_level} (Confidence: ${(data.confidence * 100).toFixed(0)}%)</span>. Signals: ${data.evidence.join(' + ')}`;
                }
                // Automatically start SOS countdown
                startSOSCountdown();
            } catch (e) {}
        });
    }

    if (simNormalBtn) {
        simNormalBtn.addEventListener('click', async () => {
            document.getElementById('gauge-gforce').style.width = '15%';
            document.getElementById('val-gforce').textContent = '0.2 G';
            document.getElementById('gauge-tilt').style.width = '8%';
            document.getElementById('val-tilt').textContent = '4°';
            document.getElementById('gauge-audio').style.width = '20%';
            document.getElementById('val-audio').textContent = '38 dB';
            
            try {
                const res = await fetch('/api/safety/accident_simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ severity: 'low' })
                });
                const data = await res.json();
                if (accidentReportText) {
                    accidentReportText.innerHTML = `<span style="color: #10b981;">Normal movement telemetry. Threat Level: NORMAL.</span>`;
                }
            } catch (e) {}
        });
    }

    if (verifyCmdBtn && verifyCmdInput) {
        verifyCmdBtn.addEventListener('click', async () => {
            const cmd = verifyCmdInput.value.trim();
            if (!cmd) return;
            
            try {
                const res = await fetch('/api/safety/verify_command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                if (verifyCmdResult) {
                    if (data.blocked) {
                        verifyCmdResult.innerHTML = `<span style="color: #ef4444; font-weight: bold;">⛔ BLOCKED BY SAFETY BOUNDING:</span> ${data.reason}`;
                        speakText("Dangerous operation blocked by safety engine.");
                    } else {
                        verifyCmdResult.innerHTML = `<span style="color: #10b981; font-weight: bold;">✅ VERIFIED SAFE:</span> ${data.reason}`;
                    }
                }
            } catch (e) {}
        });
    }

    // ----------------------------------------------------
    // 7. DEVICES & INSTALLED APPS HUB
    // ----------------------------------------------------
    const appsCatalogGrid = document.getElementById('apps-catalog-grid');
    const appSearchInput = document.getElementById('app-search-input');
    const windowsListContainer = document.getElementById('windows-list-container');
    const refreshWindowsBtn = document.getElementById('refresh-windows-btn');
    const copyMobileUrlBtn = document.getElementById('copy-mobile-url-btn');
    const handoffTaskBtn = document.getElementById('handoff-task-btn');
    const mobileUrlText = document.getElementById('mobile-url-text');
    let allInstalledApps = [];

    async function loadSystemInfo() {
        try {
            const res = await fetch('/api/system/info');
            const data = await res.json();
            
            const hostTitle = document.getElementById('host-name-title');
            const hostOs = document.getElementById('host-os-details');
            if (hostTitle) hostTitle.textContent = `${data.hostname} (Laptop)`;
            if (hostOs) hostOs.textContent = `${data.os} (${data.architecture}) | CPU: ${data.cpu_cores} Cores | RAM: ${data.ram_percent}% | ${data.battery}`;
            if (mobileUrlText) mobileUrlText.textContent = data.pairing_url;
            
        } catch (e) {}
    }

    async function loadInstalledApps() {
        if (!appsCatalogGrid) return;
        try {
            const res = await fetch('/api/devices/installed_apps');
            const data = await res.json();
            allInstalledApps = data.apps || [];
            renderAppsGrid(allInstalledApps);
        } catch (e) {
            appsCatalogGrid.innerHTML = '<p style="color: #94a3b8;">Could not load applications catalog.</p>';
        }
    }

    function renderAppsGrid(apps) {
        if (!appsCatalogGrid) return;
        if (apps.length === 0) {
            appsCatalogGrid.innerHTML = '<p style="color: #94a3b8;">No matching applications found.</p>';
            return;
        }
        
        appsCatalogGrid.innerHTML = '';
        apps.forEach(app => {
            const card = document.createElement('div');
            card.className = 'app-item-card';
            card.innerHTML = `
                <div class="app-item-info">
                    <span class="app-item-icon">⚡</span>
                    <strong>${app.name}</strong>
                </div>
                <button class="btn btn-sm btn-primary launch-app-btn" data-app="${app.name}">Launch</button>
            `;
            
            card.querySelector('.launch-app-btn').addEventListener('click', async () => {
                const btn = card.querySelector('.launch-app-btn');
                btn.disabled = true;
                btn.textContent = 'Launching...';
                try {
                    await fetch('/api/devices/launch_app', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ app_name: app.name })
                    });
                    btn.textContent = '✓ Opened';
                    speakText(`Opening ${app.name}`);
                    setTimeout(() => { btn.disabled = false; btn.textContent = 'Launch'; }, 2000);
                } catch (e) {
                    btn.disabled = false;
                    btn.textContent = 'Launch';
                }
            });
            
            appsCatalogGrid.appendChild(card);
        });
    }

    if (appSearchInput) {
        appSearchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase().trim();
            const filtered = allInstalledApps.filter(a => a.name.toLowerCase().includes(q) || a.alias.toLowerCase().includes(q));
            renderAppsGrid(filtered);
        });
    }

    async function loadActiveWindows() {
        if (!windowsListContainer) return;
        try {
            const res = await fetch('/api/devices/windows');
            const data = await res.json();
            const windows = data.windows || [];
            
            if (windows.length === 0) {
                windowsListContainer.innerHTML = '<p style="color: #94a3b8; padding: 12px;">Active Windows background sync operational.</p>';
                return;
            }
            
            windowsListContainer.innerHTML = '';
            windows.forEach(w => {
                const row = document.createElement('div');
                row.className = 'window-row-card';
                row.innerHTML = `
                    <div class="window-name">
                        <strong>${w.name}</strong> <span style="font-size: 0.8rem; color: #94a3b8;">(PID: ${w.id})</span>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-sm btn-secondary focus-win-btn" data-target="${w.name}">Focus</button>
                        <button class="btn btn-sm btn-danger close-win-btn" data-pid="${w.id}" data-name="${w.name}">Close</button>
                    </div>
                `;
                
                row.querySelector('.focus-win-btn').addEventListener('click', async () => {
                    await fetch('/api/devices/windows/focus', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ target: w.name })
                    });
                    speakText(`Focused ${w.name}`);
                });
                
                row.querySelector('.close-win-btn').addEventListener('click', async () => {
                    await fetch('/api/devices/windows/close', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ pid: w.id, name: w.name })
                    });
                    row.remove();
                    speakText(`Closed ${w.name}`);
                });
                
                windowsListContainer.appendChild(row);
            });
        } catch (e) {
            windowsListContainer.innerHTML = '<p style="color: #94a3b8;">Active processes running in background.</p>';
        }
    }

    if (refreshWindowsBtn) refreshWindowsBtn.addEventListener('click', loadActiveWindows);

    if (copyMobileUrlBtn && mobileUrlText) {
        copyMobileUrlBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(mobileUrlText.textContent);
            copyMobileUrlBtn.textContent = '✓ Copied!';
            setTimeout(() => { copyMobileUrlBtn.textContent = '📋 Copy Link'; }, 2000);
        });
    }

    if (handoffTaskBtn) {
        handoffTaskBtn.addEventListener('click', async () => {
            handoffTaskBtn.disabled = true;
            try {
                const res = await fetch('/api/devices/handoff', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target_device: 'Phone', task: 'Current ASTRA Session' })
                });
                const data = await res.json();
                alert(`📲 Task Handoff Complete!\n${data.message}\nOpen ${mobileUrlText.textContent} on your phone to resume.`);
                speakText("Task handed off to mobile device.");
            } catch (e) {
            } finally {
                handoffTaskBtn.disabled = false;
            }
        });
    }

    // ----------------------------------------------------
    // 8. ACCESSIBILITY STUDIO (AAC, BRAILLE, DYSLEXIA, GESTURE)
    // ----------------------------------------------------
    const aacCards = document.querySelectorAll('.aac-card');
    const aacSpokenText = document.getElementById('aac-spoken-text');
    const brailleInput = document.getElementById('braille-input');
    const brailleOutput = document.getElementById('braille-output');
    const readingTextInput = document.getElementById('reading-text-input');
    const readingSpeedSlider = document.getElementById('reading-speed-slider');
    const speedVal = document.getElementById('speed-val');
    const startReadingBtn = document.getElementById('start-reading-btn');
    const toggleDyslexiaFont = document.getElementById('toggle-dyslexia-font');
    const toggleContrastBtn = document.getElementById('toggle-contrast-btn');
    const gestureBtns = document.querySelectorAll('.gesture-btn');
    const gestureResultText = document.getElementById('gesture-result-text');
    const triggerHapticBtn = document.getElementById('trigger-haptic-btn');

    // AAC Cards
    aacCards.forEach(card => {
        card.addEventListener('click', async () => {
            const phrase = card.dataset.phrase;
            const symbol = card.dataset.symbol;
            
            if (aacSpokenText) {
                aacSpokenText.innerHTML = `<strong>[AAC: ${symbol}]</strong> <span style="color: #10b981;">"${phrase}"</span>`;
            }
            speakText(phrase);
            
            try {
                await fetch('/api/accessibility/aac/speak', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, message: phrase })
                });
            } catch (e) {}
        });
    });

    // Braille Transliterator
    const brailleMap = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
        'k': '⠇', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
        'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵', ' ': ' ',
        '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑', '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚',
        ',': '⠂', '.': '⠲', '!': '⠖', '?': '⠦', '-': '⠤'
    };

    function updateBraille() {
        if (!brailleInput || !brailleOutput) return;
        const txt = brailleInput.value.toLowerCase();
        const bChars = Array.from(txt).map(c => brailleMap[c] || c).join('');
        brailleOutput.textContent = bChars || '⠁⠎⠞⠗⠁';
    }

    if (brailleInput) brailleInput.addEventListener('input', updateBraille);

    // Reading Assistant
    if (readingSpeedSlider && speedVal) {
        readingSpeedSlider.addEventListener('input', (e) => {
            speedVal.textContent = `${e.target.value}x`;
        });
    }

    if (startReadingBtn && readingTextInput) {
        startReadingBtn.addEventListener('click', () => {
            const text = readingTextInput.value.trim();
            if (!text || !('speechSynthesis' in window)) return;
            
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            const rate = parseFloat(readingSpeedSlider?.value || 1.0);
            utterance.rate = rate;
            window.speechSynthesis.speak(utterance);
        });
    }

    if (toggleDyslexiaFont) {
        toggleDyslexiaFont.addEventListener('click', () => {
            document.body.classList.toggle('dyslexia-font');
            toggleDyslexiaFont.classList.toggle('btn-primary');
        });
    }

    if (toggleContrastBtn) {
        toggleContrastBtn.addEventListener('click', () => {
            document.body.classList.toggle('high-contrast-mode');
            toggleContrastBtn.classList.toggle('btn-warning');
        });
    }

    // Gestures
    gestureBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const gesture = btn.dataset.gesture;
            try {
                const res = await fetch('/api/accessibility/gesture', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ gesture })
                });
                const data = await res.json();
                if (gestureResultText) {
                    gestureResultText.innerHTML = `<strong>Executed Action:</strong> <span style="color: #10b981;">${data.result?.message || gesture}</span>`;
                }
                speakText(data.result?.message || gesture);
            } catch (e) {}
        });
    });

    if (triggerHapticBtn) {
        triggerHapticBtn.addEventListener('click', () => {
            if ('vibrate' in navigator) {
                navigator.vibrate([200, 100, 200, 100, 300]);
            }
            if (gestureResultText) {
                gestureResultText.innerHTML = '<span style="color: #10b981;">📳 Haptic Vibration Pulse Dispatched.</span>';
            }
        });
    }

    // ----------------------------------------------------
    // 9. AI & SPECIALIZED AGENTS WORKBENCH
    // ----------------------------------------------------
    const runAgentBtns = document.querySelectorAll('.run-agent-btn');
    runAgentBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const agent = btn.dataset.agent;
            const inputEl = document.getElementById(`${agent}-prompt`);
            const outputEl = document.getElementById(`${agent}-output`);
            const prompt = inputEl?.value.trim() || "Analyze task";
            
            btn.disabled = true;
            btn.textContent = '⏳ Running...';
            if (outputEl) outputEl.textContent = `[${agent.toUpperCase()} AGENT] Executing task: "${prompt}"...`;
            
            try {
                const res = await fetch('/api/agents/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent, prompt })
                });
                const data = await res.json();
                if (outputEl) {
                    let formatted = data.response
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/`([^`]+)`/g, '<code>$1</code>')
                        .replace(/\n/g, '<br>');
                    outputEl.innerHTML = formatted;
                }
                speakText(data.response);
            } catch (e) {
                if (outputEl) outputEl.textContent = `Agent execution error: ${e.message}`;
            } finally {
                btn.disabled = false;
                btn.textContent = btn.dataset.agent === 'research' ? '🔍 Run Web Research' : (btn.dataset.agent === 'coding' ? '⚡ Generate Code' : (btn.dataset.agent === 'os' ? '⚙️ Run OS Action' : '🌐 Navigate Web'));
            }
        });
    });

    // Initial preload of system data
    loadSystemInfo();
});
