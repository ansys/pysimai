.. _best_practices_geomai:

Best practices
==============

Generative Design with AI
----------------------------

The principle is that:

- Given a dataset of geometries provided by the user,
- The AI model is trained to find a compressed representation of those given geometries.
- Once the representation is computed, the model can generate new geometries by working in this compressed representation space.

This principle is based on the AI concept of latent space.


Concept of Latent Space
----------------------------

The latent space is a compressed version of complex data, converted into a representation that captures the most important features.

To generate a meaningful geometry from a latent space, it is effective to approximate its corresponding latent representation (i.e. its code)
by computing a weighted average of two codes from a code dictionary (i.e. a collection of latent codes derived from the training data).
This approach leverages the smooth structure of the latent space, where intermediate points between known latent representations
can correspond to meaningful interpolations of their associated geometries.
