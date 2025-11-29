const express = require('express');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const { Storage } = require('@google-cloud/storage');
const logger = require('./logger');

const app = express();
const port = 3002;

let storageOptions = {};
const googleApplicationCredentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

if (googleApplicationCredentialsPath) {
  storageOptions.keyFilename = googleApplicationCredentialsPath;
  logger.info(`Using GCS credentials from file: ${googleApplicationCredentialsPath}`);
} else {
  logger.error('GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Please provide the path to the service account key file.');
  process.exit(1);
}

const storage = new Storage(storageOptions);
const bucketName = process.env.GCS_BUCKET_NAME || 'your-gcs-bucket-name';
const bucket = storage.bucket(bucketName);

const upload = multer({
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 5 * 1024 * 1024, // no larger than 5mb
    },
});

// Request logging middleware
app.use((req, res, next) => {
    logger.info({ message: 'Request received', method: req.method, url: req.originalUrl, ip: req.ip });
    res.on('finish', () => {
        logger.info({
            message: 'Request finished',
            method: req.method,
            url: req.originalUrl,
            ip: req.ip,
            status: res.statusCode
        });
    });
    next();
});

// Upload endpoint
app.post('/upload', upload.single('photo'), async (req, res, next) => {
    logger.info('Upload endpoint called');
    if (!req.file) {
        logger.warn('No file uploaded');
        return res.status(400).send('No file uploaded.');
    }
    logger.info(`File uploaded: ${req.file.originalname}`);

    const blob = bucket.file(uuidv4() + req.file.originalname);
    const blobStream = blob.createWriteStream({
        resumable: false,
    });

    blobStream.on('error', err => {
        logger.error('Error uploading to GCS', err);
        next(err); 
    });

    blobStream.on('finish', () => {
        const publicUrl = `https://storage.googleapis.com/${bucket.name}/${blob.name}`;
        logger.info(`File uploaded to GCS: ${publicUrl}`);
        res.status(200).send({ url: publicUrl });
    });

    blobStream.end(req.file.buffer);
});

// Readiness Probe
app.get('/health/ready', async (req, res) => {
    logger.info('Readiness probe called');
    try {
        const [exists] = await bucket.exists();
        if (exists) {
            logger.info('GCS bucket exists');
            res.status(200).send('Ready');
        } else {
            logger.error('GCS bucket does not exist');
            res.status(503).send('Not Ready');
        }
    } catch (error) {
        logger.error('Error checking GCS bucket', error);
        res.status(503).send('Not Ready');
    }
});

// Liveness Probe
app.get('/health/live', (req, res) => {
    logger.info('Liveness probe called');
    res.status(200).send('Live');
});

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled error', err);
    res.status(500).send('Internal Server Error');
});


app.listen(port, () => {
    logger.info(`Image service listening at http://localhost:${port}`);
});
