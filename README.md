# Heron Coding Challenge - File Classifier

This is my submission for the Heron File Classifier task.

## Summary

I wanted to address each of the three core challenges: handling poorly named files, adapting to new industries and handling higher volumes.

I built a containerised app that uses OCR and PDF parsing to extract content. The classifier can be configured on a per-industry basis without code changes.

The app can be deployed today to Heroku or Fargate for load testing.

## Quick start commands

To build the container image:

```bash
$ docker build -t join-the-siege .
```

To run the image locally:

```bash
 $ docker run -p 8000:8000 join-the-siege
```

To query the endpoint:

```bash
$ curl -X POST -F 'file=@files/drivers_license_1.jpg' -F 'industry=government' http://127.0.0.1:8000/classify_file
```

(note the addition of an `industry` field in the request)

## Handling poorly named files

### Challenge

Filenames may be incorrect, misleading or simply uninformative.

### Solution

Use OCR and PDF parsing to extract the text for classification instead.

### Approach

I detect the file type using Python’s standard library `mimetypes` module and then dispatch to OCR or PDF extraction as appropriate.

For PDF extraction I chose `pdfplumber` because of its permissive licence. I avoided commercial libraries for this MVP in order to reduce friction for going live.

For OCR I chose `EasyOCR` because it is a pure-Python library with no system dependencies (such as Tesseract). This makes it easier to develop without resorting to dev containers.

### Limitations

The current implementation doesn’t extract text from scanned PDFs (e.g. those produced by iPhone’s Scan Document feature). To address this, we could switch to the `pypdf` library, which can extract images as well as text, and then run the images through OCR.

I have assumed that incoming files will have correct extensions; otherwise file type detection will not work. For greater robustness, we could use `python-magic` to inspect files.

## Adapting to new industries

### Challenge

Every industry gets the same classifier; there is no specificity for industry nuances.

The classifier can’t be configured for a new industry without code changes.

### Solution

Per-industry classifier, enabling a different set of documents, with different keywords, for each industry.

Configuration stored as YAML, suitable for sharing with non-technical stakeholders.

### Approach

I’ve added a new `industry` field to the `classify_file` endpoint, allowing the user to select their industry.

I’ve created a `classifier_rules.yaml` file to store per-industry configuration. This is checked into the repo for now, which has the benefit of keeping the syntax in sync with any code changes.

I extended the classifier to allow multiple keywords for one document type. This provides more flexibility and helps deal with issues like spelling variations (e.g. 'licence' versus 'license').

### Limitations

The YAML configuration file is lazily loaded via Python imports. If there is an error, it doesn’t surface until a request is made. Ideally, we would load the configuration at app startup and surface any errors then.

## Processing larger volumes

### Challenge

Need to handle 100,000 documents per day– that’s 1 per second, spikes could be much higher.

### Solution

Containerise the app to enable horizontal scaling.

### Approach

I containerised the app to allow easy scaling behind a load balancer. This is especially effective given the app is stateless, and well supported by PaaS services like Heroku and AWS Fargate.

I reduced container startup time by baking OCR models into the image, rather than allowing EasyOCR to download them. This allows us to scale more rapidly during traffic spikes.

I load the OCR model from disk once and re-use it for each request, reducing response times.

I enabled worker concurrency with Gunicorn to further increase throughput. This should be tuned in deployment to match memory and CPU resources.

### Limitations

Each OCR request takes ~1.5s in Docker Desktop on my Mac. With four workers it would take 10 hours to process 100,000 documents. I haven’t completed a load test on a cloud server.

Web server workers will block while waiting for the user’s file upload. This could be addressed by buffering uploads at the load balancer.

The first request after container startup is slower due to model loading. We could improve this by pre-loading the model at app startup.

## Productionising

### Operational safety

I’ve set a file size limit for uploads to guard against memory issues. In particular, `pdfplumber` will uncompress PDF contents which could create memory pressure.

There is an existing file extension check at the perimeter in `app.py`. I have left this in, even though my `file_to_text` logic is also checking file extensions for its own routing. This maintains a separate security layer before business logic. As part of hardening, I would enhance the security layer with more robust checking of uploaded files.

Before deploying to production I’d integrate our existing logging and error monitoring infrastructure.

### CI/CD and Testing

I’ve added unit tests for the new modules, covering happy path and edge cases, as well as an integration test using the provided sample files.

For an ongoing project I would set up a CI/CD pipeline to run the tests, build the Docker image and deploy to staging.

### Dependency management

I’ve frozen dependencies to `requirements.txt` to ensure reproducibility. In a full project, I’d use pip-compile or equivalent to manage dependencies, in particular separating direct and transitive requirements.

I’d also expect an automated license audit to catch any non-commercial licenses.

## Future work

### Improving classification

A simple extension to the keyword classifier would be to add scoring. For example, weighting results based on the frequency of keyword matches.

However, this effort would likely be better spent on a machine learning implementation, which I believe would perform well on this problem. I’d start with bag-of-words vectorisation into a simple linear SVC classifier (e.g. using scikit-learn). Training data could initially be sourced from real-world documents found online.

I suspect only a small amount of data would be needed to achieve useful performance, and we could begin with a hand-labelled dataset committed in the repo, training the model at container build time for simplicity.

### Enabling business configuration

In the future we could consider moving classifier configuration (or training data) into a database with a ReTool front-end that non-technical users could configure. This would allow the company to configure, improve and maintain new industry classifications without needing developer resource.

### Scaling performance

EasyOCR supports GPU acceleration via CUDA. This would provide a dramatic speed-up, given the right container environment.
