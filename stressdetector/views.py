from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os


def home(request):
    result = None
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.path(filename)

        # TODO: Run MobileNetV2 prediction here
        # For now, use dummy result
        result = {
            'stress_level': 'Medium',
            'mood_tag': 'Neutral',
            'heatmap_url': None,  # Replace with actual heatmap image path if available
        }

        # Optionally delete image after processing
        os.remove(image_path)

    return render(request, 'stressdetector/home.html', {'result': result})

