// Course Materials Admin JavaScript
// This script handles dynamic enabling/disabling of file fields based on material type

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the form behavior
    initializeFileFields();
    
    // Add event listener to material type field
    const materialTypeField = document.querySelector('select[name="material_type"]');
    if (materialTypeField) {
        materialTypeField.addEventListener('change', toggleFileFields);
    }
});

function initializeFileFields() {
    // Set initial state based on current material type selection
    toggleFileFields();
}

function toggleFileFields() {
    const materialTypeField = document.querySelector('select[name="material_type"]');
    const imageFileField = document.querySelector('input[name="image_file"]');
    const documentFileField = document.querySelector('input[name="document_file"]');
    
    if (!materialTypeField || !imageFileField || !documentFileField) {
        return;
    }
    
    const selectedType = materialTypeField.value;
    
    // Get the parent containers for styling
    const imageFieldContainer = imageFileField.closest('.form-row') || imageFileField.parentElement;
    const documentFieldContainer = documentFileField.closest('.form-row') || documentFileField.parentElement;
    
    if (selectedType === 'document') {
        // Enable document field, disable image field
        enableField(documentFileField, documentFieldContainer);
        disableField(imageFileField, imageFieldContainer);
        
        // Clear image field value
        imageFileField.value = '';
        
    } else if (selectedType === 'image') {
        // Enable image field, disable document field
        enableField(imageFileField, imageFieldContainer);
        disableField(documentFileField, documentFieldContainer);
        
        // Clear document field value
        documentFileField.value = '';
        
    } else {
        // If no type selected, disable both fields
        disableField(imageFileField, imageFieldContainer);
        disableField(documentFileField, documentFieldContainer);
    }
}

function enableField(field, container) {
    field.disabled = false;
    field.required = true;
    
    if (container) {
        container.style.opacity = '1';
        container.style.pointerEvents = 'auto';
        
        // Remove disabled styling
        container.classList.remove('disabled-field');
        
        // Add enabled styling
        container.classList.add('enabled-field');
    }
    
    // Update field label to show it's required
    const label = document.querySelector(`label[for="${field.id}"]`);
    if (label && !label.textContent.includes('*')) {
        label.innerHTML = label.textContent + ' <span style="color: red;">*</span>';
    }
}

function disableField(field, container) {
    field.disabled = true;
    field.required = false;
    
    if (container) {
        container.style.opacity = '0.6';
        container.style.pointerEvents = 'none';
        
        // Add disabled styling
        container.classList.add('disabled-field');
        container.classList.remove('enabled-field');
    }
    
    // Update field label to remove required indicator
    const label = document.querySelector(`label[for="${field.id}"]`);
    if (label) {
        label.innerHTML = label.textContent.replace(' <span style="color: red;">*</span>', '');
    }
}

// Add CSS styles for visual feedback
const style = document.createElement('style');
style.textContent = `
    .disabled-field {
        opacity: 0.6 !important;
        pointer-events: none !important;
        background-color: #fff !important;
        border: 1px dashed #ccc !important;
        border-radius: 4px !important;
        padding: 8px !important;
        margin: 4px 0 !important;
    }
    
    .enabled-field {
        opacity: 1 !important;
        pointer-events: auto !important;
        background-color: #fff !important;
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
        padding: 8px !important;
        margin: 4px 0 !important;
    }
    
    .disabled-field input[type="file"] {
        cursor: not-allowed !important;
        background-color: #fff !important;
    }
    
    .enabled-field input[type="file"] {
        cursor: pointer !important;
        background-color: #fff !important;
    }
    
    .disabled-field label {
        color: #999 !important;
        font-style: italic !important;
    }
    
    .enabled-field label {
        color: #333 !important;
        font-weight: bold !important;
    }
    
    /* Add visual indicator for required fields */
    .enabled-field label::after {
        content: " *";
        color: red;
        font-weight: bold;
    }
    
    /* Style the material type field */
    select[name="material_type"] {
        font-weight: bold;
        padding: 4px;
        border: 2px solid #007cba;
        border-radius: 4px;
    }
    
    /* Add transition effects */
    .form-row, .field-image_file, .field-document_file {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);
