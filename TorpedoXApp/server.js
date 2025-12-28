const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const multer = require('multer');


const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static('public'));

const upload = multer({
    dest: 'uploads/', // Files will be saved in the 'uploads' folder
    limits: { fileSize: 10 * 1024 * 1024 }, // Max file size: 10MB
});

// Ensure the 'uploads' folder exists
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Serve the HTML file (index.html)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Endpoint to handle file upload
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ success: false, message: 'No file uploaded' });
    }

    const file = req.file;
    const filePath = path.join(__dirname, 'uploads', file.filename);

    // Read the file and extract the text (assuming text-based file)
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading file:', err);
            return res.status(500).json({ success: false, message: 'Error reading file' });
        }

        // Debugging: Log the extracted text
        console.log('Extracted text:', data);

        if (!data || data.trim().length === 0) {
            return res.status(400).json({ success: false, message: 'No text extracted from the file' });
        }

        // Send the extracted text to the Python script for hash identification
        exec(`python ${path.join(__dirname, 'backend', 'Hash_Identification.py')} "${data}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error executing Python script: ${error.message}`);
                return res.status(500).json({ success: false, message: 'Error executing Python script' });
            }
            if (stderr) {
                console.error(`stderr: ${stderr}`);
            }

            // Send the result of the hash identification back to the frontend
            const result = stdout.trim();
            res.json({ success: true, hashResult: result, text: data });  // Include the extracted text in the response

        });


    });
});

app.post('/ml_logic', (req, res) => {
    const { text } = req.body;

    if (!text) {
        return res.status(400).json({ success: false, message: 'No text provided' });
    }

    // Path to the tester.py file
    const pythonScriptPath = path.join(__dirname, 'backend/hasher/hash/tester.py');

    // Run the Python script using child_process
    exec(`python ${pythonScriptPath} "${text}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ success: false, message: 'Error executing Python script' });
        }
    
        console.log('stdout:', stdout);  // Log stdout for better debugging
    
        try {
            const result = JSON.parse(stdout);  // Parse the output from the Python script
            res.json({ success: true, mlResult: result });
        } catch (err) {
            console.error('Error parsing result:', err);
            res.status(500).json({ success: false, message: 'Error parsing Python script result' });
        }
    });
});

app.post('/validate_hash', (req, res) => {
    const { text } = req.body;
    console.log("asdfs",text);
    // Assuming you have a Python script (hash_identification.py) to validate the text
    exec(`python ${path.join(__dirname, 'backend', 'Hash_Identification.py')} "${text}"`, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ success: false, message: 'Error validating hash' });
        }

        // Send the validation result from the Python script
        res.json({
            validationResult: stdout.trim() || stderr
        });
    });
});

// Endpoint for ClasMod
app.post('/ClasMod', (req, res) => {
    const text = req.body.text;

    // Execute Python script and pass the ciphertext directly as a command argument
    exec(`python ${path.join(__dirname, 'backend', 'ClasMod', 'tester.py')} "${text}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            res.status(500).json({ error: 'Error executing Python script.' });
            return;
        }
        if (stderr) {
            console.error(`Stderr: ${stderr}`);
        }
        console.log("ClasMod Result:", stdout);
        res.json({ result: stdout.trim() });
    });
});


// Endpoint for SymAsymTester
app.post('/SymAsymTester', (req, res) => {
    const { ciphertext } = req.body;
    const tempInputFile = path.join(__dirname,'temp_input.txt');
    const featureFile = path.join(__dirname,'feature.csv');

    // Write ciphertext to a temporary file
    fs.writeFile(tempInputFile, ciphertext, (err) => {
        if (err) {
            console.error(`File write error: ${err}`);
            res.status(500).json({ error: 'Failed to write input file.' });
            return;
        }

        // Execute Test.py
        exec(`python D:/TorpedoX/TorpedoXApp/backend/SymAsymTester/Test.py ${tempInputFile}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                res.status(500).json({ error: 'Error executing Python script.' });
                return;
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`);
            }

            // Read the feature file and process the result
            fs.readFile(featureFile, 'utf8', (readErr, data) => {
                if (readErr) {
                    console.error(`File read error: ${readErr}`);
                    res.status(500).json({ error: 'Failed to read feature file.' });
                    return;
                }

                // Return the result from the stdout of the Python script
                console.log("SymAsymTester Result:", stdout);  // Log to verify
                res.json({ result: stdout.trim() });
            });
        });
    });
});

app.post('/StreamBlockTester', (req, res) => {
    const { ciphertext } = req.body;
    const tempInputFile = path.join(__dirname, 'temp_input.txt');
    const featureFile = path.join(__dirname, 'feature.csv');

    // Write ciphertext to a temporary file
    fs.writeFile(tempInputFile, ciphertext, (err) => {
        if (err) {
            console.error(`File write error: ${err}`);
            res.status(500).json({ error: 'Failed to write input file.' });
            return;
        }

        // Execute the Python script
        exec(`python D:/TorpedoX/TorpedoXApp/backend/StreamBlockTester/Test.py ${tempInputFile}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                res.status(500).json({ error: 'Error executing Python script.' });
                return;
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`);
            }

            // Read the feature file and process the result
            fs.readFile(featureFile, 'utf8', (readErr, data) => {
                if (readErr) {
                    console.error(`File read error: ${readErr}`);
                    res.status(500).json({ error: 'Failed to read feature file.' });
                    return;
                }

                // Return the result from the Python script's stdout
                console.log("StreamBlock Result:", stdout);  // Log to verify
                res.json({ result: stdout.trim() });
            });
        });
    });
});

app.post('/StreamIdentifier', (req, res) => {
    const { ciphertext } = req.body;
    const tempInputFile = path.join(__dirname, 'temp_input.txt');
    const featureFile = path.join(__dirname, 'feature.csv');

    // Step 1: Write the ciphertext to a temporary file
    fs.writeFile(tempInputFile, ciphertext, (err) => {
        if (err) {
            console.error(`File write error: ${err}`);
            res.status(500).json({ error: 'Failed to write input file.' });
            return;
        }

        // Step 2: Execute the Python script to process the ciphertext
        exec(`python D:/TorpedoX/TorpedoXApp/backend/StreamIdentifier/Test.py ${tempInputFile}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                res.status(500).json({ error: 'Error executing Python script.' });
                return;
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`);
            }

            // Step 3: Parse the result and send it back
            const result = stdout.trim();  // Remove any extra spaces or newlines
            console.log("Stream Identifier Result:", result);  // Log the result
            res.json({ result });
        });
    });
});

app.post('/BlockIdentifier', (req, res) => {
    const { ciphertext } = req.body;
    const tempInputFile = path.join(__dirname, 'temp_input.txt');
    const featureFile = path.join(__dirname, 'feature.csv');

    // Step 1: Write the ciphertext to a temporary file
    fs.writeFile(tempInputFile, ciphertext, (err) => {
        if (err) {
            console.error(`File write error: ${err}`);
            res.status(500).json({ error: 'Failed to write input file.' });
            return;
        }

        // Step 2: Execute the Python script to process the ciphertext
        exec(`python D:/TorpedoX/TorpedoXApp/backend/BlockIdentifier/Test.py ${tempInputFile}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                res.status(500).json({ error: 'Error executing Python script.' });
                return;
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`);
            }

            // Step 3: Parse the result and send it back
            const result = stdout.trim();  // Remove any extra spaces or newlines
            console.log("Block Identifier Result:", result);  // Log the result
            res.json({ result });
        });
    });
});

app.post('/ClassicalIdentifier', (req, res) => {
    console.log(req.body); // Log the request body to inspect
    const text = req.body.text;

    if (!text || text.trim() === '') {
        return res.status(400).json({ error: 'No input provided' });
    }

    const scriptPath = path.join(__dirname, 'backend', 'ClassicalIdentifier', 'tester.py');
    const command = `python "${scriptPath}" "${text}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error.message}`);
            return res.status(500).json({ error: 'Error executing Python script.' });
        }
        if (stderr) {
            console.error(`Script stderr: ${stderr}`);
        }

        try {
            const result = JSON.parse(stdout.trim());
            res.json({ result });
        } catch (parseError) {
            console.error('Error parsing Python script output:', parseError);
            res.status(500).json({ error: 'Invalid Python script output.' });
        }
    });
});


// Start the server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
