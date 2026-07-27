import React from 'react';
import CsvUploader from './components/CsvUploader';

function App() {
  const handleDataParsed = (data) => {
    console.log("CSV Başarıyla Analiz Edildi:", data);
  };

  return (
    <div className="min-h-screen bg-slate-100 py-10">
      <header className="max-w-4xl mx-auto mb-8 text-center px-4">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
          Asenkron Paralel AutoML Servisi
        </h1>
        <p className="mt-2 text-slate-600 text-sm sm:text-base">
          Veri setinizi yükleyin, hedef değişkeni seçin ve modelleri paralel olarak eğitin.
        </p>
      </header>

      <main>
        <CsvUploader onDataParsed={handleDataParsed} />
      </main>
    </div>
  );
}

export default App;