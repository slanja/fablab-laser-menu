let motifs = [];
let cart = {};
let searchQuery = "";

async function loadMotifs() {
    try {
        // Volání tvého lokálního Python API
        const response = await fetch('http://localhost:5000/api/motifs');
        motifs = await response.json();
        renderContent();
    } catch (err) {
        console.error("Chyba při načítání menu:", err);
        renderContent();
    }
}

function renderContent() {
    const container = document.getElementById('content-area');
    container.innerHTML = "";

    const filtered = motifs.filter(m => m.id.toString().includes(searchQuery));

    if (filtered.length === 0) {
        container.innerHTML = `<div class="text-center py-20 text-gray-400 font-bold">ID "${searchQuery}" nenalezeno.</div>`;
        return;
    }

    const categories = [...new Set(filtered.map(m => m.category))];

    categories.forEach(cat => {
        const catSection = document.createElement('section');
        catSection.className = "mb-12";
        
        // Nadpis kategorie (např. Flowers)
        catSection.innerHTML = `<h2 class="fablab-font text-2xl text-gray-400 mb-6 border-b-2 border-gray-100 pb-2">${cat}</h2>`;
        
        const grid = document.createElement('div');
        grid.className = "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6";
        
        grid.innerHTML = filtered.filter(m => m.category === cat).map(m => `
            <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 flex flex-col items-center">
                <span class="text-xs font-black text-gray-400 mb-2 uppercase italic">ID ${m.id}</span>
                <div class="w-full aspect-square bg-gray-50 rounded-lg mb-4 flex items-center justify-center p-2">
                    <img src="${m.src}" alt="${m.id}" class="max-h-full opacity-90">
                </div>
                <div class="flex items-center gap-3 bg-gray-100 rounded-lg p-1 w-full justify-between">
                    <button onclick="updateQty('${m.id}', -1)" class="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm hover:bg-red-50 hover:text-red-600 text-xl font-bold">-</button>
                    <span id="qty-${m.id}" class="font-black text-lg text-gray-800">${cart[m.id] || 0}</span>
                    <button onclick="updateQty('${m.id}', 1)" class="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm hover:bg-blue-50 hover:text-blue-600 text-xl font-bold">+</button>
                </div>
            </div>
        `).join('');

        catSection.appendChild(grid);
        container.appendChild(catSection);
    });
}