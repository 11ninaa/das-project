import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

/**
 * Export data to CSV format
 * @param {Array<Object>} data - Array of objects to export
 * @param {string} filename - Name of the file (without extension)
 */
export const exportToCSV = (data, filename = 'export') => {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  const headers = Object.keys(data[0]);
  
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, `${filename}.csv`);
};

/**
 * Export chart/image to PDF
 */
export const exportChartToPDF = async (elementIdOrElement, filename = 'chart', title = 'Chart') => {
  try {
    const element = typeof elementIdOrElement === 'string' 
      ? document.getElementById(elementIdOrElement)
      : elementIdOrElement;

    if (!element) {
      alert('Element not found for export');
      return;
    }

    const canvas = await html2canvas(element, {
      backgroundColor: '#1e293b', // slate-800
      scale: 2, // Higher quality
      logging: false,
      useCORS: true,
    });

    const imgWidth = canvas.width;
    const imgHeight = canvas.height;
    const pdfWidth = 210; // A4 width in mm
    const pdfHeight = (imgHeight * pdfWidth) / imgWidth;
    const maxHeight = 297; // A4 height in mm

    const pdf = new jsPDF('p', 'mm', 'a4');
    
    pdf.setFontSize(16);
    pdf.text(title, 105, 15, { align: 'center' });
    
    if (pdfHeight > maxHeight) {
      const scaledHeight = maxHeight - 20; // Leave margin for title
      const scaledWidth = (imgWidth * scaledHeight) / imgHeight;
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 20, scaledWidth, scaledHeight);
    } else {
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 20, pdfWidth - 20, pdfHeight);
    }

    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error exporting to PDF:', error);
    alert('Failed to export chart to PDF');
  }
};

/**
 * Export multiple charts to a single PDF

 */
export const exportMultipleChartsToPDF = async (charts, filename = 'report') => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    let yPosition = 15;
    const pageWidth = 210;
    const pageHeight = 297;
    const margin = 10;

    for (let i = 0; i < charts.length; i++) {
      const { id, title } = charts[i];
      const element = document.getElementById(id);

      if (!element) {
        console.warn(`Element with id ${id} not found`);
        continue;
      }

      const canvas = await html2canvas(element, {
        backgroundColor: '#1e293b',
        scale: 2,
        logging: false,
        useCORS: true,
      });

      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const imgAspectRatio = imgWidth / imgHeight;
      const availableWidth = pageWidth - (margin * 2);
      const availableHeight = pageHeight - yPosition - margin;
      let imgWidthMM = availableWidth;
      let imgHeightMM = availableWidth / imgAspectRatio;

      if (imgHeightMM > availableHeight) {
        imgHeightMM = availableHeight;
        imgWidthMM = availableHeight * imgAspectRatio;
      }

      if (i > 0 && yPosition + imgHeightMM > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }

      pdf.setFontSize(14);
      pdf.text(title, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 8;

      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', margin, yPosition, imgWidthMM, imgHeightMM);
      yPosition += imgHeightMM + 10;

      if (yPosition > pageHeight - 50 && i < charts.length - 1) {
        pdf.addPage();
        yPosition = margin;
      }
    }

    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error exporting multiple charts to PDF:', error);
    alert('Failed to export charts to PDF');
  }
};


