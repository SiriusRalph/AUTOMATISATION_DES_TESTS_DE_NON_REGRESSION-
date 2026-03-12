
        document.addEventListener('DOMContentLoaded', function() {
            // File upload interaction
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');

            if (uploadArea && fileInput) {
                uploadArea.addEventListener('click', function() {
                    fileInput.click();
                });

                fileInput.addEventListener('change', function() {
                    if (this.files.length > 0) {
                        const fileName = this.files[0].name;
                        uploadArea.innerHTML = `
                            <i class="fas fa-check-circle file-upload-icon" style="color: var(--primary);"></i>
                            <div class="file-upload-text" style="color: var(--primary);">${fileName}</div>
                            <div class="file-upload-subtext">Prêt à être importé</div>
                        `;
                    }
                });

                // Drag and drop functionality
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    uploadArea.addEventListener(eventName, preventDefaults, false);
                });

                function preventDefaults(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }

                ['dragenter', 'dragover'].forEach(eventName => {
                    uploadArea.addEventListener(eventName, highlight, false);
                });

                ['dragleave', 'drop'].forEach(eventName => {
                    uploadArea.addEventListener(eventName, unhighlight, false);
                });

                function highlight() {
                    uploadArea.style.borderColor = 'var(--primary)';
                    uploadArea.style.backgroundColor = 'rgba(193, 39, 45, 0.05)';
                }

                function unhighlight() {
                    uploadArea.style.borderColor = 'var(--gray-300)';
                    uploadArea.style.backgroundColor = 'white';
                }

                uploadArea.addEventListener('drop', function(e) {
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    fileInput.files = files;

                    if (files.length > 0) {
                        const fileName = files[0].name;
                        uploadArea.innerHTML = `
                            <i class="fas fa-check-circle file-upload-icon" style="color: var(--primary);"></i>
                            <div class="file-upload-text" style="color: var(--primary);">${fileName}</div>
                            <div class="file-upload-subtext">Prêt à être importé</div>
                        `;
                    }
                });
            }

            // Mobile sidebar toggle
            const sidebar = document.querySelector('.sidebar');
            document.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    if (e.target.closest('.sidebar') || e.target.hasAttribute('data-section')) {
                        return;
                    }
                    sidebar.classList.remove('active');
                }
            });

            // Navigation between sections
            const navLinks = document.querySelectorAll('[data-section]');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Remove active class from all links
                    navLinks.forEach(navLink => {
                        navLink.classList.remove('active');
                    });

                    // Add active class to clicked link
                    this.classList.add('active');

                    // For mobile, close sidebar after selection
                    if (window.innerWidth <= 768) {
                        sidebar.classList.remove('active');
                    }
                });
            });

        });

document.addEventListener('DOMContentLoaded', function() {
    // Initialize both paginations
    initTestResultsPagination();
    initScriptsPagination();

    // User dropdown toggle
    const toggle = document.querySelector(".user-dropdown-toggle");
    const menu = document.querySelector(".user-dropdown-menu");

    if (toggle && menu) {
        toggle.addEventListener("click", function(e) {
            e.stopPropagation();
            menu.style.display = menu.style.display === "block" ? "none" : "block";
        });

        window.addEventListener("click", function() {
            menu.style.display = "none";
        });
    }
});

// Test Results Pagination
function initTestResultsPagination() {
    const itemsPerPage = 5;
    let currentPage = 1;
    let totalItems = 0;

    // Elements
    const prevBtn = document.querySelector('.test-prev');
    const nextBtn = document.querySelector('.test-next');
    const refreshBtn = document.querySelector('.test-refresh');
    const infoElement = document.querySelector('.test-pagination-info');
    const tbody = document.querySelector('.test-results-body');

    // Load initial results
    loadTestResults();

    // Event listeners
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadTestResults();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentPage < Math.ceil(totalItems / itemsPerPage)) {
            currentPage++;
            loadTestResults();
        }
    });

    refreshBtn.addEventListener('click', () => {
        loadTestResults();
    });

    async function loadTestResults() {
        try {
            // Show loading state
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Chargement...</td></tr>';
            prevBtn.disabled = true;
            nextBtn.disabled = true;
            infoElement.textContent = 'Chargement...';

            const response = await fetch(`/get_test_results?page=${currentPage}&per_page=${itemsPerPage}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load test results');
            }

            totalItems = data.data.total;
            updateTestResultsTable(data.data.results);
            updatePaginationInfo(infoElement, prevBtn, nextBtn, currentPage, totalItems, 'Résultats');
        } catch (error) {
            console.error('Error loading test results:', error);
            tbody.innerHTML = `<tr><td colspan="6" class="text-center error">Erreur: ${error.message}</td></tr>`;
            infoElement.textContent = 'Erreur de chargement';
        }
    }

    function updateTestResultsTable(results) {
        tbody.innerHTML = '';

        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Aucun résultat trouvé</td></tr>';
            return;
        }

        results.forEach(result => {
            const row = document.createElement('tr');

            let statusClass, statusIcon;
            if (result.status === 'Réussi') {
                statusClass = 'success';
                statusIcon = 'fa-check-circle';
            } else if (result.status === 'Échoué') {
                statusClass = 'danger';
                statusIcon = 'fa-times-circle';
            } else {
                statusClass = 'warning';
                statusIcon = 'fa-spinner fa-pulse';
            }

            row.innerHTML = `
                <td>#${result.id}</td>
                <td class="truncate">${result.script_name}</td>
                <td>${result.browser}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        <i class="fas ${statusIcon}"></i> ${result.status}
                    </span>
                </td>
                <td>${result.date}</td>
                <td>
                    <form method="post" action="/view_result_detail">
                        <input type="hidden" name="script_name" value="${result.script_name}">
                        <input type="hidden" name="date" value="${result.date}">
                        <button class="btn btn-sm btn-outline">
                            <i class="fas fa-eye"></i>
                        </button>
                    </form>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Scripts Pagination
function initScriptsPagination() {
    const itemsPerPage = 5;
    let currentPage = 1;
    let totalItems = 0;

    // Elements
    const prevBtn = document.querySelector('.script-prev');
    const nextBtn = document.querySelector('.script-next');
    const infoElement = document.querySelector('.script-pagination-info');
    const scriptList = document.querySelector('.script-list');

    // Load initial scripts
    loadScripts();

    // Event listeners
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadScripts();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentPage < Math.ceil(totalItems / itemsPerPage)) {
            currentPage++;
            loadScripts();
        }
    });

    async function loadScripts() {
        try {
            // Show loading state
            scriptList.innerHTML = '<div class="empty-state">Chargement...</div>';
            prevBtn.disabled = true;
            nextBtn.disabled = true;
            infoElement.textContent = 'Chargement...';

            const response = await fetch(`/get_scripts?page=${currentPage}&per_page=${itemsPerPage}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to load scripts');
            }

            totalItems = data.data.total;
            updateScriptsList(data.data.scripts);
            updatePaginationInfo(infoElement, prevBtn, nextBtn, currentPage, totalItems, 'Scripts');
        } catch (error) {
            console.error('Error loading scripts:', error);
            scriptList.innerHTML = `<div class="empty-state error">Erreur: ${error.message}</div>`;
            infoElement.textContent = 'Erreur de chargement';
        }
    }

    function updateScriptsList(scripts) {
        scriptList.innerHTML = '';

        if (scripts.length === 0) {
            scriptList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>Aucun script trouvé</p>
                </div>
            `;
            return;
        }

        scripts.forEach(file => {
            const item = document.createElement('div');
            item.className = 'script-item';
            item.innerHTML = `
                <span class="script-name">${file}</span>
                <form method="GET" action="/download_script/${file}">
                    <button type="submit" class="btn btn-sm btn-secondary">
                        <i class="fas fa-download"></i>
                    </button>
                </form>
            `;
            scriptList.appendChild(item);
        });
    }
}

// Common pagination function
function updatePaginationInfo(infoElement, prevBtn, nextBtn, currentPage, totalItems, label) {
    const itemsPerPage = 5;
    const start = ((currentPage - 1) * itemsPerPage) + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);

    infoElement.textContent = `${label} ${start}-${end} sur ${totalItems}`;

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === Math.ceil(totalItems / itemsPerPage);
}