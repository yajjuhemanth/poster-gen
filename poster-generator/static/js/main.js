class PosterGenerator {
            constructor() {
                this.form = document.getElementById('posterForm');
                this.loadingSection = document.getElementById('loadingSection');
                this.loadingText = document.getElementById('loadingText');
                this.enhancedPromptSection = document.getElementById('enhancedPromptSection');
                this.promptDisplay = document.getElementById('promptDisplay');
                this.resultsSection = document.getElementById('resultsSection');
                this.posterGrid = document.getElementById('posterGrid');
                this.generateBtn = document.getElementById('generateBtn');
                
                this.init();
            }

            init() {
                this.form.addEventListener('submit', this.handleSubmit.bind(this));
                this.setupFileUpload();
                this.addInputAnimations();
            }

            setupFileUpload() {
                const fileInput = document.getElementById('logoUpload');
                const fileLabel = document.querySelector('.file-upload-label');
                
                fileInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        fileLabel.innerHTML = `
                            <i class="fas fa-check-circle" style="color: #4ade80;"></i>
                            <div>
                                <div style="font-weight: 600;">${file.name}</div>
                                <div style="font-size: 0.9rem; color: var(--text-secondary);">File selected successfully</div>
                            </div>
                        `;
                        fileLabel.style.borderColor = '#4ade80';
                                                fileLabel.style.background = 'rgba(74, 222, 128, 0.1)';
                    }
                });
            }

            addInputAnimations() {
                const inputs = document.querySelectorAll('.form-input');
                inputs.forEach(input => {
                    input.addEventListener('focus', () => {
                        input.parentElement.classList.add('focused');
                    });
                    input.addEventListener('blur', () => {
                        input.parentElement.classList.remove('focused');
                    });
                });
            }

            async handleSubmit(event) {
                event.preventDefault();

                const prompt = document.getElementById('promptInput').value.trim();
                const aspectRatio = document.getElementById('aspectRatio').value;
                const logoFile = document.getElementById('logoUpload').files[0];

                if (!prompt) return;

                this.showLoading("Enhancing your prompt with AI...");

                try {
                    // Mocking AI-enhanced prompt for now
                    const enhancedPrompt = await this.enhancePrompt(prompt, aspectRatio);
                    
                    this.showEnhancedPrompt(enhancedPrompt);
                    this.showLoading("Generating poster...");

                    const posters = await this.generatePosters(enhancedPrompt, aspectRatio, logoFile);

                    this.showPosters(posters);
                } catch (error) {
                    console.error("Error generating poster:", error);
                    alert("Something went wrong while generating your poster.");
                } finally {
                    this.hideLoading();
                }
            }


            async enhancePrompt(prompt, aspectRatio) {
                // Call backend to enhance prompt
                const response = await fetch('/enhance-prompt', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ prompt })
                });
                if (!response.ok) {
                    throw new Error('Failed to enhance prompt');
                }
                const data = await response.json();
                if (data.enhanced_prompt) {
                    return data.enhanced_prompt;
                } else {
                    throw new Error(data.error || 'No enhanced prompt returned');
                }
            }

            async generatePosters(prompt, aspectRatio, logoFile) {
                // Use FormData to send logo file if present
                const formData = new FormData();
                formData.append('prompt', prompt);
                formData.append('aspect_ratio', aspectRatio);
                if (logoFile) {
                    formData.append('logo', logoFile);
                }
                const response = await fetch('/generate-poster', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    throw new Error('Failed to generate posters');
                }
                const data = await response.json();
                if (data.posters) {
                    // Return array of base64 images
                    return data.posters.map(p => `data:image/png;base64,${p.image}`);
                } else {
                    throw new Error(data.error || 'No posters returned');
                }
            }

            showLoading(text) {
                this.loadingText.textContent = text;
                this.loadingSection.style.display = 'block';
                this.resultsSection.style.display = 'none';
                this.enhancedPromptSection.style.display = 'none';
            }

            hideLoading() {
                this.loadingSection.style.display = 'none';
            }

            showEnhancedPrompt(prompt) {
                this.promptDisplay.textContent = prompt;
                this.enhancedPromptSection.style.display = 'block';
            }

            showPosters(images) {
                this.posterGrid.innerHTML = '';
                const logoFile = document.getElementById('logoUpload').files[0];
                images.forEach((src, idx) => {
                    const card = document.createElement('div');
                    card.classList.add('poster-card');
                    card.style.position = 'relative';
                    card.innerHTML = `
                        <img src="${src}" alt="Poster Image" class="poster-image" />
                        <div class="poster-controls">
                            <a href="${src}" class="btn btn-secondary" download target="_blank">
                                <i class="fas fa-download"></i> Download
                            </a>
                        </div>
                    `;
                    // If a logo was uploaded, show an 'Add Logo Overlay' button (but do not add overlay yet)
                    if (logoFile) {
                        const addBtn = document.createElement('button');
                        addBtn.className = 'btn btn-primary';
                        addBtn.textContent = 'Add Logo Overlay';
                        addBtn.style.marginTop = '10px';
                        addBtn.type = 'button';
                        addBtn.onclick = () => {
                            // Only add overlay if not already present
                            if (!card.querySelector('.logo-overlay')) {
                                const overlay = document.createElement('img');
                                overlay.src = URL.createObjectURL(logoFile);
                                overlay.className = 'logo-overlay';
                                overlay.style.position = 'absolute';
                                overlay.style.left = '30px';
                                overlay.style.top = '30px';
                                overlay.style.width = '20%';
                                overlay.style.cursor = 'grab';
                                overlay.style.zIndex = 10;
                                overlay.draggable = false;
                                card.appendChild(overlay);
                                makeOverlayDraggable(overlay, card);

                                // Add apply overlay & download button if not already present
                                if (!card.querySelector('.apply-overlay-btn')) {
                                    const applyBtn = document.createElement('button');
                                    applyBtn.className = 'btn btn-primary apply-overlay-btn';
                                    applyBtn.textContent = 'Apply Overlay & Download';
                                    applyBtn.style.marginTop = '10px';
                                    applyBtn.type = 'button';
                                    applyBtn.onclick = () => {
                                        this.applyOverlayAndDownload(card, overlay, src);
                                    };
                                    card.querySelector('.poster-controls').appendChild(applyBtn);
                                }
                            }
                        };
                        card.querySelector('.poster-controls').appendChild(addBtn);
                    }
                    this.posterGrid.appendChild(card);
                });
                this.resultsSection.style.display = 'block';
            }
        }

        // Place these outside the class definition

        // Helper to make overlay draggable
        function makeOverlayDraggable(overlayImg, posterCard) {
            let isDragging = false;
            let offsetX = 0, offsetY = 0;
            overlayImg.addEventListener('mousedown', function(e) {
                isDragging = true;
                const rect = overlayImg.getBoundingClientRect();
                offsetX = e.clientX - rect.left;
                offsetY = e.clientY - rect.top;
                overlayImg.style.cursor = 'grabbing';
                e.preventDefault();
            });
            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                const parentRect = posterCard.getBoundingClientRect();
                let x = e.clientX - parentRect.left - offsetX;
                let y = e.clientY - parentRect.top - offsetY;
                // Clamp within poster
                x = Math.max(0, Math.min(x, parentRect.width - overlayImg.width));
                y = Math.max(0, Math.min(y, parentRect.height - overlayImg.height));
                overlayImg.style.left = x + 'px';
                overlayImg.style.top = y + 'px';
            });
            document.addEventListener('mouseup', function() {
                if (isDragging) {
                    isDragging = false;
                    overlayImg.style.cursor = 'grab';
                }
            });
        }

        // Apply overlay and download composited image
        PosterGenerator.prototype.applyOverlayAndDownload = function(card, overlayImg, posterSrc) {
            const posterImg = card.querySelector('.poster-image');
            // Create a canvas with poster size
            const canvas = document.createElement('canvas');
            canvas.width = posterImg.naturalWidth;
            canvas.height = posterImg.naturalHeight;
            const ctx = canvas.getContext('2d');
            // Draw poster
            ctx.drawImage(posterImg, 0, 0, canvas.width, canvas.height);
            // Draw overlay at correct position/size
            // Calculate overlay position/size relative to poster
            const posterRect = posterImg.getBoundingClientRect();
            const overlayRect = overlayImg.getBoundingClientRect();
            const x = ((overlayRect.left - posterRect.left) / posterRect.width) * canvas.width;
            const y = ((overlayRect.top - posterRect.top) / posterRect.height) * canvas.height;
            const w = (overlayRect.width / posterRect.width) * canvas.width;
            const h = (overlayRect.height / posterRect.height) * canvas.height;
            // Draw overlay
            const tempLogo = new window.Image();
            tempLogo.onload = function() {
                ctx.drawImage(tempLogo, x, y, w, h);
                // Download
                const link = document.createElement('a');
                link.download = 'poster_with_logo.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            };
            tempLogo.src = overlayImg.src;
        };

        function showTutorial() {
            alert("🎥 Tutorial Coming Soon!\nThis will guide you on how to create amazing posters using the tool.");
        }

        // Initialize the Poster Generator
        document.addEventListener('DOMContentLoaded', () => {
            new PosterGenerator();
        });
