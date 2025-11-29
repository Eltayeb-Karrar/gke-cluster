const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const logger = require('./logger');
const promBundle = require('express-prom-bundle');

const app = express();
const port = 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/iam-service';

mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => logger.info('MongoDB connected'))
    .catch(err => logger.error('MongoDB connection error:', err));

const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true }
});

const User = mongoose.model('User', UserSchema);

app.use(bodyParser.json());
app.use(promBundle({includeMethod: true, includePath: true}));

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

// Register endpoint
app.post('/register', async (req, res, next) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(400).send('Username and password are required');
        }
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = new User({ username, password: hashedPassword });
        await user.save();
        logger.info(`User created: ${username}`);
        res.status(201).send('User created');
    } catch (error) {
        if (error.code === 11000) {
            logger.warn(`Registration failed: Username already exists - ${req.body.username}`);
            return res.status(409).send('Username already exists');
        }
        next(error);
    }
});

// Login endpoint
app.post('/login', async (req, res, next) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username });

        if (user && await bcrypt.compare(password, user.password)) {
            const token = jwt.sign({ id: user._id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
            logger.info(`User logged in: ${username}`);
            res.json({ token });
        } else {
            logger.warn(`Invalid login attempt for username: ${username}`);
            res.status(401).send('Invalid credentials');
        }
    } catch (error) {
        next(error);
    }
});

// Validate token endpoint
app.post('/validate', (req, res) => {
    const { token } = req.body;
    if (!token) {
        logger.warn('Token validation attempt with no token provided');
        return res.status(401).send('No token provided');
    }

    jwt.verify(token, JWT_SECRET, (err, decoded) => {
        if (err) {
            logger.warn('Invalid token provided for validation');
            return res.status(401).send('Invalid token');
        }
        logger.info(`Token validated for user: ${decoded.username}`);
        res.json({ valid: true, user: decoded });
    });
});

// Logout endpoint (simplified)
app.post('/logout', (req, res) => {
    logger.info('User logged out');
    res.send('Logged out successfully');
});

// Readiness Probe
app.get('/health/ready', (req, res) => {
    if (mongoose.connection.readyState === 1) {
        logger.info('Readiness probe successful');
        res.status(200).send('Ready');
    } else {
        logger.error('Readiness probe failed: MongoDB not connected');
        res.status(503).send('Not Ready');
    }
});

// Liveness Probe
app.get('/health/live', (req, res) => {
    logger.info('Liveness probe successful');
    res.status(200).send('Live');
});

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled error', err);
    res.status(500).send('Internal Server Error');
});


app.listen(port, () => {
    logger.info(`IAM service listening at http://localhost:${port}`);
});
