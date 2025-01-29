document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.querySelector("#resumeTable tbody");
    const modal = document.getElementById("detailsModal");
    const modalContent = document.getElementById("modalContent");
    const closeModal = document.querySelector(".close");
    const filterBtn = document.getElementById("filterBtn");
    const filterPanel = document.getElementById("filterPanel");
    const applyFiltersBtn = document.getElementById("applyFilters");
    const clearFiltersBtn = document.getElementById("clearFilters");

    // Initialize DataTable
    $(document).ready(function () {
        $('#resumeTable').DataTable();
    });

    // Fetch data from the backend
    fetch(`/results?file_path=CV.pdf`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                alert("Error: " + data.error);
                return;
            }

            const { details, sections } = data;

           document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.querySelector("#resumeTable tbody");
    const modal = document.getElementById("detailsModal");
    const modalContent = document.getElementById("modalContent");
    const closeModal = document.querySelector(".close");
    const filterBtn = document.getElementById("filterBtn");
    const filterPanel = document.getElementById("filterPanel");
    const applyFiltersBtn = document.getElementById("applyFilters");
    const clearFiltersBtn = document.getElementById("clearFilters");

    // Initialize DataTable
    $(document).ready(function () {
        $('#resumeTable').DataTable();
    });

    // Fetch data from the backend
    fetch(`/results?file_path=CV.pdf`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                alert("Error: " + data.error);
                return;
            }

            const { details, sections } = data;

            // Populate the table
            const row = `  
                <tr>
                    <td>${details["Name"] || "N/A"}</td>
                    <td>${details["Age"] || "N/A"}</td>
                    <td>${details["Phone Number"] || "N/A"}</td>
                    <td>${details["Email Address"] || "N/A"}</td>
                    <td>${sections["Experience"] ? sections["Experience"].join(", ") : "N/A"}</td>
                    <td>${details["Current Company"] || "N/A"}</td>
                    <td>${sections["Skills"] ? sections["Skills"].join(", ") : "N/A"}</td>
                    <td>${sections["Projects"] ? sections["Projects"].join(", ") : "N/A"}</td>
                    <td>${details["Address/Location"] || "N/A"}</td>
                    <td>${details["LinkedIn Profile"] ? `<a href="${details["LinkedIn Profile"]}" target="_blank">${details["LinkedIn Profile"]}</a>` : "N/A"}</td>
                    <td><button class="view-details-btn">View Details</button></td>
                </tr>
            `;
            tableBody.innerHTML = row;

            // Add event listener for "View Details" button
            document.querySelector(".view-details-btn").addEventListener("click", () => {
                modalContent.innerHTML = `
                    <h3>Personal Details</h3>
                    <ul>
                        ${Object.entries(details).map(([key, value]) => `<li><strong>${key}:</strong> ${value}</li>`).join("")}
                    </ul>
                    <h3>Resume Sections</h3>
                    ${Object.entries(sections).map(([key, value]) => `<h4>${key}</h4><p>${value.join("<br>")}</p>`).join("")}
                `;
                modal.style.display = "block";
            });
        })
        .catch(error => console.error("Error fetching data:", error));

    // Close modal functionality
    closeModal.onclick = () => (modal.style.display = "none");
    window.onclick = event => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Export to Excel
    document.getElementById("exportExcel").addEventListener("click", () => {
        const table = document.getElementById("resumeTable");
        const workbook = XLSX.utils.table_to_book(table);
        XLSX.writeFile(workbook, "Resume_Details.xlsx");
    });

    // Clear table data
    document.getElementById("clearData").addEventListener("click", () => {
        tableBody.innerHTML = "";
    });

    // Toggle filter panel visibility
    filterBtn.addEventListener("click", () => {
        filterPanel.classList.toggle("show"); // Add or remove "show" class to toggle visibility
    });

    // Apply filters to the DataTable
    const table = $('#resumeTable').DataTable();
    
    applyFiltersBtn.addEventListener("click", function () {
        const minAge = parseInt(document.getElementById("minAge").value) || 0;
        const maxAge = parseInt(document.getElementById("maxAge").value) || 999;
        const skills = document.getElementById("skillsFilter").value.toLowerCase().split(",").map(s => s.trim());
        const location = document.getElementById("locationFilter").value.toLowerCase();

        // Reset previous search filters
        $.fn.dataTable.ext.search = [];

        // Add custom filter to DataTable
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            const age = parseInt(data[1]) || 0; // Assuming age is in the second column
            const rowSkills = data[9].toLowerCase(); // Assuming skills are in the 10th column
            const rowLocation = data[8].toLowerCase(); // Assuming location is in the 9th column

            // Return true if row passes the filter, false otherwise
            return (
                age >= minAge &&
                age <= maxAge &&
                (!skills.length || skills.some(skill => rowSkills.includes(skill))) &&
                (!location || rowLocation.includes(location))
            );
        });

        // Redraw table with filters applied
        table.draw();
    });

    // Clear filters and reset the DataTable
    clearFiltersBtn.addEventListener("click", function () {
        document.getElementById("minAge").value = "";
        document.getElementById("maxAge").value = "";
        document.getElementById("skillsFilter").value = "";
        document.getElementById("locationFilter").value = "";

        // Clear all filters and redraw table
        $.fn.dataTable.ext.search = [];
        table.draw();
    });
});

            tableBody.innerHTML = row;

            // Add event listener for "View Details" button
            document.querySelector(".view-details-btn").addEventListener("click", () => {
                modalContent.innerHTML = `
                    <h3>Personal Details</h3>
                    <ul>
                        ${Object.entries(details).map(([key, value]) => `<li><strong>${key}:</strong> ${value}</li>`).join("")}
                    </ul>
                    <h3>Resume Sections</h3>
                    ${Object.entries(sections).map(([key, value]) => `<h4>${key}</h4><p>${value.join("<br>")}</p>`).join("")}
                `;
                modal.style.display = "block";
            });
        })
        .catch(error => console.error("Error fetching data:", error));

    // Close modal functionality
    closeModal.onclick = () => (modal.style.display = "none");
    window.onclick = event => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Export to Excel
    document.getElementById("exportExcel").addEventListener("click", () => {
        const table = document.getElementById("resumeTable");
        const workbook = XLSX.utils.table_to_book(table);
        XLSX.writeFile(workbook, "Resume_Details.xlsx");
    });

    // Clear table data
    document.getElementById("clearData").addEventListener("click", () => {
        tableBody.innerHTML = "";
    });

    // Toggle filter panel
    filterBtn.addEventListener("click", () => {
        filterPanel.classList.toggle("show");
    });

    // Apply filters
    const table = $('#resumeTable').DataTable();
    
    applyFiltersBtn.addEventListener("click", function () {
        const minAge = parseInt(document.getElementById("minAge").value) || 0;
        const maxAge = parseInt(document.getElementById("maxAge").value) || 999;
        const skills = document.getElementById("skillsFilter").value.toLowerCase().split(",").map(s => s.trim());
        const location = document.getElementById("locationFilter").value.toLowerCase();

        // Reset previous search filters
        $.fn.dataTable.ext.search = [];

        // Add custom filter to DataTable
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            const age = parseInt(data[1]) || 0; // Assuming age is in the second column
            const rowSkills = data[9].toLowerCase(); // Assuming skills are in the 10th column
            const rowLocation = data[8].toLowerCase(); // Assuming location is in the 9th column

            // Return true if row passes the filter, false otherwise
            return (
                age >= minAge &&
                age <= maxAge &&
                (!skills.length || skills.some(skill => rowSkills.includes(skill))) &&
                (!location || rowLocation.includes(location))
            );
        });

        // Redraw table with filters applied
        table.draw();
    });

    // Clear filters
    clearFiltersBtn.addEventListener("click", function () {
        document.getElementById("minAge").value = "";
        document.getElementById("maxAge").value = "";
        document.getElementById("skillsFilter").value = "";
        document.getElementById("locationFilter").value = "";

        // Clear all filters and redraw table
        $.fn.dataTable.ext.search = [];
        table.draw();
    });
});
