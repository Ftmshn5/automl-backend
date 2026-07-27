import React, { useState } from 'react';
import Papa from 'papaparse';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

export default function CsvUploader({ onDataParsed }) {
  const [fileInfo, setFileInfo] = useState(null);
  const [columns, setColumns] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [previewData, setPreviewData] = useState([]);
  const [error, setError] = useState('');

  const handleFile = (file) => {
    setError('');
    
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      setError('Lütfen geçerli bir .CSV dosyası yükleyin!');
      return;
    }

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      preview: 5,
      complete: (results) => {
        if (results.meta.fields && results.meta.fields.length > 0) {
          setColumns(results.meta.fields);
          setPreviewData(results.data);
          setFileInfo({
            name: file.name,
            size: (file.size / 1024).toFixed(2) + ' KB'
          });
          
          if (onDataParsed) {
            onDataParsed({
              file,
              columns: results.meta.fields,
              preview: results.data
            });
          }
        } else {
          setError('CSV dosyası boş veya sütun bilgisi okunamadı.');
        }
      },
      error: (err) => {
        setError('CSV dosyası okunurken hata oluştu: ' + err.message);
      }
    });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    handleFile(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      
      {/* Sürükle - Bırak Alanı */}
      <div 
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-slate-300 hover:border-indigo-500 bg-slate-50 hover:bg-indigo-50/30 rounded-xl p-8 text-center transition-all cursor-pointer group"
      >
        <input 
          type="file" 
          accept=".csv"
          onChange={(e) => handleFile(e.target.files[0])}
          className="hidden" 
          id="csv-input"
        />
        <label htmlFor="csv-input" className="cursor-pointer flex flex-col items-center">
          <UploadCloud className="w-12 h-12 text-slate-400 group-hover:text-indigo-600 mb-3 transition-colors" />
          <p className="text-slate-700 font-medium text-lg">
            CSV dosyanızı buraya sürükleyin veya <span className="text-indigo-600 underline">dosya seçin</span>
          </p>
          <p className="text-slate-400 text-sm mt-1">Sadece .csv uzantılı veri setleri desteklenmektedir.</p>
        </label>
      </div>

      {/* Hata Mesajı */}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Dosya Bilgisi, Target Seçimi ve Önizleme */}
      {fileInfo && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
          
          <div className="flex items-center justify-between border-b pb-4">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-indigo-600" />
              <div>
                <h3 className="font-semibold text-slate-800">{fileInfo.name}</h3>
                <p className="text-xs text-slate-500">Boyut: {fileInfo.size}</p>
              </div>
            </div>
            <span className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">
              <CheckCircle2 className="w-3.5 h-3.5" /> Yüklendi
            </span>
          </div>

          {/* Target (Hedef Değişken) Seçimi */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-700">
              🎯 Target (Hedef Değişken) Seçiniz:
            </label>
            <p className="text-xs text-slate-500">
              AutoML modellerinin tahmin etmesini istediğiniz hedef sütunu seçin.
            </p>
            <select
              value={selectedTarget}
              onChange={(e) => setSelectedTarget(e.target.value)}
              className="w-full md:w-1/2 p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="">-- Sütun Seçiniz --</option>
              {columns.map((col, idx) => (
                <option key={idx} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          {/* Veri Önizleme Tablosu */}
          {previewData.length > 0 && (
            <div className="space-y-3 pt-2">
              <h4 className="text-sm font-semibold text-slate-700">Veri Seti Önizlemesi (İlk 5 Satır)</h4>
              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="min-w-full divide-y divide-slate-200 text-sm text-left">
                  <thead className="bg-slate-100 text-slate-700">
                    <tr>
                      {columns.map((col, idx) => (
                        <th 
                          key={idx} 
                          className={`px-4 py-2 font-medium ${col === selectedTarget ? 'bg-indigo-100 text-indigo-900 font-bold' : ''}`}
                        >
                          {col} {col === selectedTarget && '🎯'}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    {previewData.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-50">
                        {columns.map((col, cIdx) => (
                          <td 
                            key={cIdx} 
                            className={`px-4 py-2 whitespace-nowrap text-slate-600 ${col === selectedTarget ? 'bg-indigo-50/50 font-medium text-indigo-900' : ''}`}
                          >
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}