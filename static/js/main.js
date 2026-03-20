/**
 * Main JS file for Zomin E'lonlar
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // Page Loader
    const pageLoader = document.getElementById('page-loader');
    if (pageLoader) {
        setTimeout(() => {
            pageLoader.style.opacity = '0';
            setTimeout(() => {
                pageLoader.style.display = 'none';
            }, 500);
        }, 300); // Quick fade out for smooth appearance
    }

    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileNav = document.getElementById('mobile-nav');
    
    if (mobileMenuBtn && mobileNav) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileNav.classList.toggle('open');
            const icon = mobileMenuBtn.querySelector('i');
            if (mobileNav.classList.contains('open')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // File Upload Preview & Drag and Drop
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    
    if (dropArea && fileInput && imagePreview) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropArea.classList.add('dragover');
        }

        function unhighlight(e) {
            dropArea.classList.remove('dragover');
        }

        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                fileInput.files = files;
                handleFiles(files[0]);
            }
        }
        
        // Handle select files
        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                handleFiles(this.files[0]);
            }
        });

        function handleFiles(file) {
            // Check file type
            if (!file.type.match('image.*')) {
                alert('Faqat rasm fayllarini yuklashingiz mumkin (JPG, PNG, WEBP).');
                return;
            }
            
            // Check file size (16MB max)
            if (file.size > 16 * 1024 * 1024) {
                alert('Rasm hajmi juda katta. Iltimos 16MB dan kichik rasm yuklang.');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('d-none');
                uploadPlaceholder.style.display = 'none';
            }
            reader.readAsDataURL(file);
        }
    }
    
    // Auto-dismiss Alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Find close button
        const closeBtn = alert.querySelector('.close-btn');
        if (closeBtn) {
            // Automatically remove complete alert node after 5 seconds to keep DOM clean
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });

    // Form Client-side Validation (Simple)
    const addListingForm = document.getElementById('addListingForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (addListingForm) {
        addListingForm.addEventListener('submit', function(e) {
            // Basic check
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yuklanmoqda...';
            submitBtn.disabled = true;
        });
    }

});
