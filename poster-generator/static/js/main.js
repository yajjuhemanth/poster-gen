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
                <div class="overlay-container" style="position:relative;display:inline-block;">
                    <img src="${src}" alt="Poster Image" class="poster-image" style="display:block;max-width:100%;height:auto;" />
                </div>
                <div class="poster-controls">
                    <button class="btn btn-primary download-btn" type="button" style="margin-top: 10px;">
                        <i class="fas fa-download"></i> Download with Logo
                    </button>
                    <div class="download-status" style="margin-top: 8px; font-size: 0.9rem; color: #666;"></div>
                </div>
            `;
            
            const overlayContainer = card.querySelector('.overlay-container');
            const posterImg = overlayContainer.querySelector('.poster-image');
            const downloadBtn = card.querySelector('.download-btn');
            const downloadStatus = card.querySelector('.download-status');
            
            let overlay = null;
            let logoImgLoaded = false;
            let posterImgLoaded = false;

            // Helper to enable download only when all images are loaded
            function checkReady() {
                if ((logoFile ? logoImgLoaded : true) && posterImgLoaded) {
                    downloadBtn.disabled = false;
                    downloadStatus.textContent = logoFile ? 'Logo positioned - Ready to download' : 'Ready to download';
                    downloadStatus.style.color = '#4ade80';
                }
            }

            // Poster image load handling
            posterImg.onload = () => {
                posterImgLoaded = true;
                checkReady();
            };
            
            if (posterImg.complete) {
                posterImgLoaded = true;
                checkReady();
            }

            // Add logo overlay if logo file exists
            if (logoFile) {
                overlay = document.createElement('img');
                overlay.src = URL.createObjectURL(logoFile);
                overlay.className = 'logo-overlay';
                overlay.style.position = 'absolute';
                // Place at top-right with margin
                overlay.style.right = '20px';
                overlay.style.top = '20px';
                overlay.style.left = '';
                overlay.style.bottom = '';
                overlay.style.width = '20%';
                overlay.style.cursor = 'grab';
                overlay.style.zIndex = 10;
                overlay.style.border = '2px dashed rgba(255,255,255,0.5)';
                overlay.style.borderRadius = '4px';
                overlay.draggable = false;
                overlay.crossOrigin = 'anonymous';
                
                overlay.onload = () => {
                    logoImgLoaded = true;
                    checkReady();
                };
                
                if (overlay.complete) {
                    logoImgLoaded = true;
                    checkReady();
                }
                
                overlayContainer.appendChild(overlay);
                
                // Make overlay draggable and resizable
                this.makeOverlayDraggable(overlay, overlayContainer, downloadStatus);
            }

            // Download button click handler
            downloadBtn.onclick = () => {
                this.downloadPosterWithLogo(overlayContainer, downloadBtn, downloadStatus, idx);
            };

            this.posterGrid.appendChild(card);
        });
        
        this.resultsSection.style.display = 'block';
    }

    // Enhanced draggable functionality with better feedback
    makeOverlayDraggable(overlayImg, posterContainer, statusElement) {
        let isDragging = false;
        let offsetX = 0, offsetY = 0;
        let isResizing = false;
        let startWidth = 0, startHeight = 0, startMouseX = 0, startMouseY = 0;

        // Add resize handle
        const resizeHandle = document.createElement('div');
        resizeHandle.style.position = 'absolute';
        resizeHandle.style.right = '-8px';
        resizeHandle.style.bottom = '-8px';
        resizeHandle.style.width = '16px';
        resizeHandle.style.height = '16px';
        resizeHandle.style.background = '#4ade80';
        resizeHandle.style.borderRadius = '50%';
        resizeHandle.style.cursor = 'nwse-resize';
        resizeHandle.style.zIndex = 20;
        resizeHandle.style.border = '2px solid white';
        resizeHandle.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
        resizeHandle.title = 'Resize logo';
        overlayImg.parentElement.appendChild(resizeHandle);

        // Position indicator
        const positionIndicator = document.createElement('div');
        positionIndicator.style.position = 'absolute';
        positionIndicator.style.top = '-25px';
        positionIndicator.style.left = '0';
        positionIndicator.style.background = 'rgba(0,0,0,0.8)';
        positionIndicator.style.color = 'white';
        positionIndicator.style.padding = '2px 6px';
        positionIndicator.style.borderRadius = '4px';
        positionIndicator.style.fontSize = '11px';
        positionIndicator.style.display = 'none';
        positionIndicator.style.zIndex = 25;
        overlayImg.parentElement.appendChild(positionIndicator);

        // Resize handle mousedown
        resizeHandle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startWidth = overlayImg.offsetWidth;
            startHeight = overlayImg.offsetHeight;
            startMouseX = e.clientX;
            startMouseY = e.clientY;
            statusElement.textContent = 'Resizing logo...';
            statusElement.style.color = '#f59e0b';
            e.stopPropagation();
            e.preventDefault();
        });

        // Overlay mousedown for dragging
        overlayImg.addEventListener('mousedown', (e) => {
            if (isResizing) return;
            isDragging = true;
            const rect = overlayImg.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            overlayImg.style.cursor = 'grabbing';
            overlayImg.style.border = '2px dashed #4ade80';
            positionIndicator.style.display = 'block';
            statusElement.textContent = 'Positioning logo...';
            statusElement.style.color = '#f59e0b';
            e.preventDefault();
        });

        // Mouse move handler
        document.addEventListener('mousemove', (e) => {
            if (isResizing) {
                const dx = e.clientX - startMouseX;
                const dy = e.clientY - startMouseY;
                const newWidth = Math.max(24, startWidth + dx);
                const newHeight = Math.max(24, startHeight + dy);
                overlayImg.style.width = newWidth + 'px';
                overlayImg.style.height = newHeight + 'px';
                statusElement.textContent = `Size: ${Math.round(newWidth)}x${Math.round(newHeight)}px`;
                return;
            }
            
            if (!isDragging) return;
            
            const parentRect = posterContainer.getBoundingClientRect();
            let x = e.clientX - parentRect.left - offsetX;
            let y = e.clientY - parentRect.top - offsetY;
            
            // Clamp within poster bounds
            x = Math.max(0, Math.min(x, parentRect.width - overlayImg.offsetWidth));
            y = Math.max(0, Math.min(y, parentRect.height - overlayImg.offsetHeight));
            
            overlayImg.style.left = x + 'px';
            overlayImg.style.top = y + 'px';
            
            // Update position indicator
            positionIndicator.textContent = `${Math.round(x)}, ${Math.round(y)}`;
        });

        // Mouse up handler
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                overlayImg.style.cursor = 'grab';
                overlayImg.style.border = '2px dashed rgba(255,255,255,0.5)';
                positionIndicator.style.display = 'none';
                statusElement.textContent = 'Logo positioned - Ready to download';
                statusElement.style.color = '#4ade80';
            }
            if (isResizing) {
                isResizing = false;
                statusElement.textContent = 'Logo resized - Ready to download';
                statusElement.style.color = '#4ade80';
            }
        });
    }

    // Enhanced download functionality with better error handling and feedback
    async downloadPosterWithLogo(overlayContainer, downloadBtn, statusElement, posterIndex) {
        try {
            const posterImg = overlayContainer.querySelector('.poster-image');
            const logoImg = overlayContainer.querySelector('.logo-overlay');
            
            // Validate images are loaded
            if (!posterImg.complete || (logoImg && !logoImg.complete)) {
                statusElement.textContent = 'Please wait for all images to load';
                statusElement.style.color = '#ef4444';
                return;
            }

            // Update UI to show download is in progress
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing Download...';
            statusElement.textContent = 'Creating composite image...';
            statusElement.style.color = '#f59e0b';

            // Visual feedback - briefly highlight the logo
            if (logoImg) {
                logoImg.style.boxShadow = '0 0 20px rgba(74, 222, 128, 0.8)';
                logoImg.style.transition = 'box-shadow 0.3s ease';
            }

            // Wait for visual feedback
            await new Promise(resolve => setTimeout(resolve, 300));

            // Create high-quality canvas for final composite
            const canvas = document.createElement('canvas');
            canvas.width = posterImg.naturalWidth;
            canvas.height = posterImg.naturalHeight;
            const ctx = canvas.getContext('2d');
            
            // Set high quality rendering
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';

            // Draw the poster as background
            ctx.drawImage(posterImg, 0, 0, canvas.width, canvas.height);

            // Draw logo overlay if present
            if (logoImg) {
                const posterRect = posterImg.getBoundingClientRect();
                const logoRect = logoImg.getBoundingClientRect();
                const containerRect = overlayContainer.getBoundingClientRect();
                
                // Calculate scaling factors
                const scaleX = canvas.width / posterRect.width;
                const scaleY = canvas.height / posterRect.height;
                
                // Calculate logo position and size in canvas coordinates
                const logoX = (logoRect.left - containerRect.left) * scaleX;
                const logoY = (logoRect.top - containerRect.top) * scaleY;
                const logoWidth = logoRect.width * scaleX;
                const logoHeight = logoRect.height * scaleY;
                
                // Draw logo with antialiasing
                ctx.drawImage(logoImg, logoX, logoY, logoWidth, logoHeight);
                
                statusElement.textContent = `Logo positioned at (${Math.round(logoX)}, ${Math.round(logoY)})`;
            }

            // Generate download with timestamp
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const fileName = `poster_${posterIndex + 1}_${timestamp}.png`;
            
            // Create and trigger download
            const link = document.createElement('a');
            link.download = fileName;
            link.href = canvas.toDataURL('image/png', 1.0);
            link.click();

            // Success feedback
            statusElement.textContent = `Downloaded: ${fileName}`;
            statusElement.style.color = '#4ade80';
            
            // Remove highlight effect
            if (logoImg) {
                logoImg.style.boxShadow = 'none';
            }

            // Reset button after short delay
            setTimeout(() => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download with Logo';
                statusElement.textContent = 'Ready for next download';
            }, 2000);

        } catch (error) {
            console.error('Download error:', error);
            statusElement.textContent = 'Download failed. Please try again.';
            statusElement.style.color = '#ef4444';
            
            // Reset button
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download with Logo';
        }
    }
}

// Tutorial function
function showTutorial() {
    alert("🎥 Tutorial Coming Soon!\nThis will guide you on how to create amazing posters using the tool.");
}

// Initialize the Poster Generator
document.addEventListener('DOMContentLoaded', () => {
    new PosterGenerator();
});