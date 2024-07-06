function addCell(tr, content, colSpan = 1) {
    let td = document.createElement('th');
    td.colSpan = colSpan;
    td.textContent = content;
    tr.appendChild(td);
}

function initializeDataTables() {
    // Cari semua tabel dengan ID yang dimulai dengan "tabel"
    document.querySelectorAll('table[id^="tabel"]').forEach(table => {
        new DataTable(table, {
            order: [[1, 'asc']],
            rowGroup: {
                startRender: null,
                endRender: function (rows, group) {
                    let valueTotal = rows
                        .data()
                        .pluck(5) // Kolom "Nilai"
                        .reduce((a, b) => a + parseFloat(b.replace(/[^\d,-]/g, '').replace(',', '.')), 0);
                    let valueSisa = rows
                        .data()
                        .pluck(9) // Kolom "Nilai"
                        .reduce((a, b) => a + parseFloat(b.replace(/[^\d,-]/g, '').replace(',', '.')), 0);

                    // Format total nilai sebagai mata uang Rupiah
                    valueTotal = new Intl.NumberFormat('id-ID', {
                        minimumFractionDigits: 2
                    }).format(valueTotal);
                    valueSisa = new Intl.NumberFormat('id-ID', {
                        minimumFractionDigits: 2
                    }).format(valueSisa);

                    // Buat baris subtotal
                    let tr = document.createElement('tr');

                    addCell(tr, 'Subtotal ' + group, 5);
                    addCell(tr, valueTotal, 1); // Total nilai
                    addCell(tr, '', 3); // Total nilai
                    addCell(tr, valueSisa, 1); // Total nilai
                    addCell(tr, '', 2); // Total nilai

                    return tr;
                },
                dataSrc: [2, 3]
            },
            lengthMenu: [
                [10, 25, 50, -1],
                [10, 25, 50, 'All']
            ],
            scrollX: true,
            scrollY: true,
        });
    });
}

// Panggil fungsi inisialisasi ketika dokumen selesai dimuat
document.addEventListener("DOMContentLoaded", function() {
    initializeDataTables();
});



