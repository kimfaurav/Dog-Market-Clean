#!/usr/bin/env node
/**
 * Export Reveal.js deck to PDF using Playwright
 * Usage: node scripts/export-pdf.js
 *
 * Requires: npm install (installs playwright)
 * Then: npx playwright install chromium
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const DECK_URL = 'http://localhost:8000/index.html?print-pdf';
const OUTPUT_PATH = path.join(__dirname, '..', 'deck.pdf');
const PORT = 8000;

async function startServer() {
    return new Promise((resolve, reject) => {
        const server = spawn('npx', ['serve', '.', '-p', PORT.toString()], {
            cwd: path.join(__dirname, '..'),
            stdio: ['ignore', 'pipe', 'pipe']
        });

        server.stdout.on('data', (data) => {
            if (data.toString().includes('Accepting connections')) {
                resolve(server);
            }
        });

        server.stderr.on('data', (data) => {
            // serve outputs to stderr for some messages
            if (data.toString().includes('Accepting connections')) {
                resolve(server);
            }
        });

        // Give it time to start
        setTimeout(() => resolve(server), 2000);
    });
}

async function exportPDF() {
    console.log('Starting local server...');
    const server = await startServer();

    try {
        console.log('Launching browser...');
        const browser = await chromium.launch();
        const page = await browser.newPage();

        // Set viewport for 16:9 aspect ratio
        await page.setViewportSize({ width: 1920, height: 1080 });

        console.log(`Loading ${DECK_URL}...`);
        await page.goto(DECK_URL, { waitUntil: 'networkidle', timeout: 60000 });

        // Wait for Reveal.js to initialize
        await page.waitForFunction(() => {
            return window.Reveal && window.Reveal.isReady && window.Reveal.isReady();
        }, { timeout: 30000 });

        // Additional wait for fonts and images
        await page.waitForTimeout(2000);

        console.log(`Exporting to ${OUTPUT_PATH}...`);
        await page.pdf({
            path: OUTPUT_PATH,
            width: '1920px',
            height: '1080px',
            printBackground: true,
            preferCSSPageSize: true
        });

        await browser.close();
        console.log(`PDF exported successfully: ${OUTPUT_PATH}`);

    } finally {
        server.kill();
    }
}

exportPDF().catch(err => {
    console.error('Export failed:', err);
    process.exit(1);
});
