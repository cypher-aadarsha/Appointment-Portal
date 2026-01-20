class NepaliCalendar {
    constructor() {
        // Reference: 1 Baisakh 2082 = 14 April 2025
        this.refBSYear = 2082;
        this.refADDate = new Date(2025, 3, 14); // Month is 0-indexed (3=April)
        
        // Days in months for 2082 BS (Approx)
        this.bsDays = [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30];
        this.bsMonths = [
            'Baisakh', 'Jestha', 'Ashadh', 'Shrawan', 'Bhadra', 'Ashwin', 
            'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra'
        ];
        
        // AD Months
        this.adMonths = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
    }

    getADDate(bsMonth, bsDay) {
        // Calculate days offset from 1 Baisakh
        let daysOffset = 0;
        for (let i = 0; i < bsMonth; i++) {
            daysOffset += this.bsDays[i];
        }
        daysOffset += (bsDay - 1);
        
        let result = new Date(this.refADDate);
        result.setDate(result.getDate() + daysOffset);
        return result;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const calendar = new NepaliCalendar();
    
    // State
    let currentBSMonth = 9; // Magh (Index 9) - Starting approx Jan/Feb
    let currentBSYear = 2082;
    let selectedDateAPiformat = null;
    let selectedMinisterId = null;

    // DOM Elements
    const grid = document.getElementById('calendar-grid');
    const monthBSDisplay = document.getElementById('current-month-bs');
    const monthADDisplay = document.getElementById('current-month-ad');
    const prevBtn = document.getElementById('prev-month');
    const nextBtn = document.getElementById('next-month');
    const ministerSelect = document.getElementById('minister-select');
    const ministerInfo = document.getElementById('minister-info');
    const slotContainer = document.getElementById('slot-container');
    const slotsList = document.getElementById('slots-list');
    
    // Initialize
    renderCalendar();

    // Event Listeners
    prevBtn.addEventListener('click', () => {
        if (currentBSMonth > 0) {
            currentBSMonth--;
            renderCalendar();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentBSMonth < 11) {
            currentBSMonth++;
            renderCalendar();
        }
    });

    ministerSelect.addEventListener('change', (e) => {
        selectedMinisterId = e.target.value;
        const option = e.target.selectedOptions[0];
        
        // Show Minister Info
        document.getElementById('minister-name').textContent = option.textContent.trim();
        document.getElementById('minister-desc').textContent = option.dataset.desc;
        const imgUrl = option.dataset.img;
        if(imgUrl) {
            document.getElementById('minister-img').src = imgUrl;
        }
        ministerInfo.classList.remove('hidden');

        // Reset slots if date already selected
        if (selectedDateAPiformat) {
            fetchSlots(selectedDateAPiformat);
        }
    });

    function renderCalendar() {
        // Clear old days (keep headers)
        const headers = Array.from(document.querySelectorAll('.weekday'));
        grid.innerHTML = '';
        headers.forEach(h => grid.appendChild(h));

        // Update Headers
        monthBSDisplay.textContent = `${calendar.bsMonths[currentBSMonth]} ${currentBSYear}`;
        
        // Calculate Start Day of Week for 1st of this BS Month
        // Get AD Date for 1st of current BS Month
        const firstDayAD = calendar.getADDate(currentBSMonth, 1);
        const startDayOfWeek = firstDayAD.getDay(); // 0=Sun, 1=Mon...
        
        // End Date AD for display range
        const totalDays = calendar.bsDays[currentBSMonth];
        const lastDayAD = calendar.getADDate(currentBSMonth, totalDays);

        monthADDisplay.textContent = `${calendar.adMonths[firstDayAD.getMonth()]} / ${calendar.adMonths[lastDayAD.getMonth()]} ${firstDayAD.getFullYear()}`;

        // Empty cells for offset
        for (let i = 0; i < startDayOfWeek; i++) {
            const empty = document.createElement('div');
            empty.className = 'day-cell empty';
            grid.appendChild(empty);
        }

        // Days
        for (let d = 1; d <= totalDays; d++) {
            const cell = document.createElement('div');
            cell.className = 'day-cell';
            
            const adDate = calendar.getADDate(currentBSMonth, d);
            const adDateString = adDate.getDate(); // Just the number
            
            // Format for API: YYYY-MM-DD
            const yyyy = adDate.getFullYear();
            const mm = String(adDate.getMonth() + 1).padStart(2, '0');
            const dd = String(adDate.getDate()).padStart(2, '0');
            const apiDate = `${yyyy}-${mm}-${dd}`;

            cell.innerHTML = `
                <div class="bs-date">${d}</div>
                <div class="ad-date">${adDateString}</div>
            `;

            cell.addEventListener('click', () => {
                document.querySelectorAll('.day-cell').forEach(c => c.classList.remove('selected'));
                cell.classList.add('selected');
                selectedDateAPiformat = apiDate;
                document.getElementById('selected-date-display').textContent = `${d} ${calendar.bsMonths[currentBSMonth]} (AD: ${apiDate})`;
                fetchSlots(apiDate);
            });

            grid.appendChild(cell);
        }
    }

    async function fetchSlots(date) {
        if (!selectedMinisterId) {
            alert("Please select a minister first.");
            return;
        }

        slotContainer.classList.remove('hidden');
        slotsList.innerHTML = 'Loading...';

        try {
            const response = await fetch(`/appointments/api/slots/?minister_id=${selectedMinisterId}&date=${date}`);
            const data = await response.json();

            slotsList.innerHTML = '';
            if (data.slots && data.slots.length > 0) {
                data.slots.forEach(slot => {
                    const el = document.createElement('div');
                    el.className = 'slot-item';
                    el.textContent = `${slot.start_time} - ${slot.end_time}`;
                    el.onclick = () => {
                        document.querySelectorAll('.slot-item').forEach(s => s.classList.remove('selected'));
                        el.classList.add('selected');
                        document.getElementById('selected-slot-id').value = slot.id;
                        document.getElementById('booking-form-container').classList.remove('hidden');
                    };
                    slotsList.appendChild(el);
                });
            } else {
                slotsList.innerHTML = '<p class="text-muted">No available slots for this date.</p>';
            }
        } catch (error) {
            slotsList.innerHTML = '<p style="color:red">Error loading slots.</p>';
        }
    }
});
