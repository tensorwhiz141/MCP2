/**
 * MongoDB Connection Utility for Netlify Functions
 * Manages connections to MongoDB for the BlackHole Agent System
 */
const mongoose = require('mongoose');

// Connection cache
let cachedConnection = null;
let connectionAttemptInProgress = false;
let autoConnectInitiated = false;

// Define MongoDB schema indexes
const createIndexes = async (db) => {
  try {
    // Create indexes for agent_results collection
    const agentResultsCollection = db.collection('agent_results');
    await agentResultsCollection.createIndex({ agent: 1 });
    await agentResultsCollection.createIndex({ created_at: 1 });
    await agentResultsCollection.createIndex({ 'input.file.name': 1 });
    await agentResultsCollection.createIndex({ 'output.extracted_text': 'text' });

    console.log('MongoDB indexes created successfully');
  } catch (error) {
    console.error('Error creating MongoDB indexes:', error);
  }
};

/**
 * Connect to MongoDB
 * @param {string} uri - MongoDB connection URI
 * @param {Object} options - Connection options
 * @returns {Promise<mongoose.Connection>} - MongoDB connection
 */
async function connectToMongoDB(uri, options = {}) {
  // If we already have a connection, return it
  if (cachedConnection && mongoose.connection.readyState === 1) {
    return cachedConnection;
  }

  // If a connection attempt is already in progress, wait for it
  if (connectionAttemptInProgress) {
    console.log('Connection attempt already in progress, waiting...');
    // Wait for the connection attempt to complete (max 3 seconds)
    for (let i = 0; i < 30; i++) {
      await new Promise(resolve => setTimeout(resolve, 100));
      if (cachedConnection && mongoose.connection.readyState === 1) {
        return cachedConnection;
      }
    }
  }

  // Mark that a connection attempt is in progress
  connectionAttemptInProgress = true;

  // Default options
  const defaultOptions = {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000, // Reduced timeout
    socketTimeoutMS: 10000, // Reduced timeout
    connectTimeoutMS: 5000, // Reduced timeout
    retryWrites: true,
    maxPoolSize: 5 // Reduced pool size
  };

  // Merge options
  const connectionOptions = { ...defaultOptions, ...options };

  try {
    // Connect to MongoDB with a timeout
    const connectionPromise = async () => {
      try {
        return await mongoose.connect(uri, connectionOptions);
      } catch (error) {
        console.error('Error in mongoose.connect:', error);
        throw error;
      }
    };

    // Add a timeout to the connection promise
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error('MongoDB connection timeout'));
      }, 5000); // 5 second timeout
    });

    // Race the connection promise against the timeout
    const connection = await Promise.race([connectionPromise(), timeoutPromise]);

    // Cache the connection
    cachedConnection = connection;

    // Set up event handlers
    mongoose.connection.on('error', (err) => {
      console.error('MongoDB connection error:', err);
      cachedConnection = null;
      connectionAttemptInProgress = false;

      // Try to reconnect after a delay
      setTimeout(() => {
        console.log('Attempting to reconnect to MongoDB...');
        connectToMongoDB(uri, options).catch(err => {
          console.error('Reconnection attempt failed:', err);
        });
      }, 5000);
    });

    mongoose.connection.on('disconnected', () => {
      console.warn('MongoDB disconnected');
      cachedConnection = null;
      connectionAttemptInProgress = false;

      // Try to reconnect after a delay
      setTimeout(() => {
        console.log('Attempting to reconnect to MongoDB...');
        connectToMongoDB(uri, options).catch(err => {
          console.error('Reconnection attempt failed:', err);
        });
      }, 5000);
    });

    mongoose.connection.on('connected', () => {
      console.log('MongoDB connected');
      connectionAttemptInProgress = false;
    });

    // Create indexes in the background
    setTimeout(() => {
      createIndexes(mongoose.connection.db)
        .then(() => console.log('MongoDB indexes created'))
        .catch(err => console.error('Error creating MongoDB indexes:', err));
    }, 100);

    console.log('Connected to MongoDB');
    connectionAttemptInProgress = false;

    return connection;
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    cachedConnection = null;
    connectionAttemptInProgress = false;

    // Return a mock connection for fallback
    return {
      connection: {
        db: getMockDb(),
        readyState: 0
      }
    };
  }
}

/**
 * Get a mock database object for fallback
 * @returns {Object} - Mock database object
 */
function getMockDb() {
  return {
    collection: (name) => ({
      find: () => ({
        limit: () => ({
          toArray: async () => []
        })
      }),
      findOne: async () => null,
      insertOne: async () => ({ insertedId: `mock_${Date.now()}` }),
      createIndex: async () => null
    }),
    listCollections: () => ({
      toArray: async () => []
    }),
    command: async () => ({ ok: 1 })
  };
}

/**
 * Get the MongoDB connection status
 * @returns {Object} - Connection status
 */
function getConnectionStatus() {
  const states = {
    0: 'disconnected',
    1: 'connected',
    2: 'connecting',
    3: 'disconnecting',
    99: 'uninitialized'
  };

  const readyState = mongoose.connection.readyState;

  return {
    status: states[readyState] || 'unknown',
    readyState: readyState,
    host: mongoose.connection.host,
    name: mongoose.connection.name,
    cached: !!cachedConnection,
    autoConnectInitiated: autoConnectInitiated
  };
}

/**
 * Close the MongoDB connection
 * @returns {Promise<void>}
 */
async function closeConnection() {
  if (mongoose.connection.readyState !== 0) {
    await mongoose.connection.close();
    cachedConnection = null;
    console.log('MongoDB connection closed');
  }
}

/**
 * Auto-connect to MongoDB using environment variables
 * This function will be called automatically when the module is imported
 * @returns {Promise<mongoose.Connection>} - MongoDB connection
 */
async function autoConnect() {
  if (autoConnectInitiated) {
    return cachedConnection;
  }

  autoConnectInitiated = true;
  console.log('Auto-connecting to MongoDB...');

  try {
    // Get MongoDB URI from environment variables
    const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/blackhole';

    console.log('Using MongoDB URI:', uri ? 'URI is set' : 'Using default URI');

    // Connect to MongoDB with a timeout
    const connectionPromise = connectToMongoDB(uri);
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error('Auto-connection timeout'));
      }, 5000); // 5 second timeout
    });

    // Race the connection promise against the timeout
    const connection = await Promise.race([connectionPromise, timeoutPromise])
      .catch(error => {
        console.error('Auto-connection failed:', error.message);
        return null;
      });

    if (connection) {
      console.log('Auto-connection to MongoDB successful');
    } else {
      console.warn('Auto-connection to MongoDB failed, using mock connection');
    }

    return connection;
  } catch (error) {
    console.error('Auto-connection to MongoDB failed:', error);
    return null;
  }
}

// Start auto-connection process
autoConnect().catch(err => {
  console.error('Error in auto-connect process:', err);
});

module.exports = {
  connectToMongoDB,
  getConnectionStatus,
  closeConnection,
  autoConnect
};
