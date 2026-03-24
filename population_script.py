import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelshare.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files import File
from users.models import Profile, Follow
from posts.models import Post, Tag, Like, Comment, Bookmark


IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "population_images")


def populate():
    print("Populating TravelShare...")

    # --- Users ---
    users_data = [
        {
            "username": "emma_explorer",
            "email": "emma@example.com",
            "password": "testpass123",
            "first_name": "Emma",
            "last_name": "Wilson",
            "bio": "University student & budget traveller. Always looking for the next adventure!",
            "location": "London, UK",
            "website": "https://emmatravels.blog",
        },
        {
            "username": "ryan_photo",
            "email": "ryan@example.com",
            "password": "testpass123",
            "first_name": "Ryan",
            "last_name": "Chen",
            "bio": "Amateur photographer documenting my trips around the world.",
            "location": "Glasgow, UK",
            "website": "",
        },
        {
            "username": "sophia_adventures",
            "email": "sophia@example.com",
            "password": "testpass123",
            "first_name": "Sophia",
            "last_name": "Martinez",
            "bio": "Travel community lover. I follow creators with great stories!",
            "location": "Barcelona, Spain",
            "website": "",
        },
        {
            "username": "alex_wander",
            "email": "alex@example.com",
            "password": "testpass123",
            "first_name": "Alex",
            "last_name": "Kim",
            "bio": "Backpacker & food lover. Sharing hidden gems around Asia.",
            "location": "Seoul, South Korea",
            "website": "https://alexwanders.com",
        },
        {
            "username": "lily_adventures",
            "email": "lily@example.com",
            "password": "testpass123",
            "first_name": "Lily",
            "last_name": "Thompson",
            "bio": "Nature enthusiast capturing landscapes and wildlife.",
            "location": "Edinburgh, UK",
            "website": "",
        },
    ]

    created_users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            print(f"  Created user: {user.username}")
        else:
            print(f"  User already exists: {user.username}")

        profile = user.profile
        profile.bio = data["bio"]
        profile.location = data["location"]
        profile.website = data["website"]
        profile.save()

        created_users.append(user)

    emma, ryan, sophia, alex, lily = created_users

    # --- Tags ---
    tag_names = [
        "sunset", "travel", "photography", "foodie", "architecture",
        "nature", "cityscape", "hiking", "streetfood", "culture",
        "mountains",
    ]
    tags = {}
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name)
        tags[name] = tag
    print(f"  Created {len(tags)} tags")

    # --- Posts (1 per user, with real images) ---
    posts_data = [
        {
            "author": ryan,
            "description": "Golden hour at Tower Bridge. The light was absolutely perfect today.",
            "location": "London, UK",
            "category": "photography",
            "tags": ["sunset", "photography", "cityscape"],
            "image_file": "tower_bridge.jpg",
        },
        {
            "author": emma,
            "description": "Found this incredible street art in Barcelona. The colours are unreal!",
            "location": "Barcelona, Spain",
            "category": "travel",
            "tags": ["travel", "culture", "streetfood"],
            "image_file": "barcelona_street_art.jpg",
        },
        {
            "author": alex,
            "description": "Best ramen I have ever had. This tiny shop in Shibuya is a must visit.",
            "location": "Tokyo, Japan",
            "category": "food",
            "tags": ["foodie", "streetfood", "travel"],
            "image_file": "tokyo_ramen.jpg",
        },
        {
            "author": lily,
            "description": "Morning hike in the Scottish Highlands. Misty mountains and complete silence.",
            "location": "Scottish Highlands, UK",
            "category": "nature",
            "tags": ["nature", "hiking", "mountains"],
            "image_file": "scottish_highlands.jpg",
        },
        {
            "author": sophia,
            "description": "The architecture in Prague is like stepping into a fairytale.",
            "location": "Prague, Czech Republic",
            "category": "architecture",
            "tags": ["architecture", "travel", "cityscape"],
            "image_file": "prague_architecture.jpg",
        },
    ]

    created_posts = []
    for i, data in enumerate(posts_data):
        image_path = os.path.join(IMAGES_DIR, data["image_file"])
        if not os.path.exists(image_path):
            print(f"  ERROR: Image not found: {image_path}")
            print(f"  Make sure the 'population_images' folder is next to this script.")
            return

        with open(image_path, "rb") as f:
            post = Post(
                author=data["author"],
                description=data["description"],
                location=data["location"],
                category=data["category"],
            )
            post.image.save(data["image_file"], File(f), save=True)

        for tag_name in data["tags"]:
            post.tags.add(tags[tag_name])
        created_posts.append(post)
        print(f"  Created post {i+1}: {data['author'].username} — {data['location']}")

    post_ryan, post_emma, post_alex, post_lily, post_sophia = created_posts

    # --- Follows ---
    follow_pairs = [
        (emma, ryan),
        (emma, sophia),
        (emma, alex),
        (ryan, emma),
        (ryan, lily),
        (sophia, ryan),
        (sophia, emma),
        (sophia, alex),
        (sophia, lily),
        (alex, ryan),
        (alex, lily),
        (lily, emma),
        (lily, ryan),
        (lily, sophia),
    ]
    for follower, following in follow_pairs:
        Follow.objects.get_or_create(follower=follower, following=following)
    print(f"  Created {len(follow_pairs)} follow relationships")

    # --- Likes ---
    like_pairs = [
        (emma, post_ryan),
        (emma, post_alex),
        (emma, post_lily),
        (ryan, post_emma),
        (ryan, post_lily),
        (sophia, post_ryan),
        (sophia, post_alex),
        (sophia, post_emma),
        (alex, post_ryan),
        (alex, post_sophia),
        (lily, post_ryan),
        (lily, post_emma),
    ]
    for user, post in like_pairs:
        Like.objects.get_or_create(user=user, post=post)
    print(f"  Created {len(like_pairs)} likes")

    # --- Comments (2 per post = 10 total) ---
    comments_data = [
        (emma, post_ryan, "Stunning shot! The lighting is perfect."),
        (sophia, post_ryan, "Tower Bridge never gets old. Great capture!"),
        (ryan, post_emma, "Barcelona is on my bucket list!"),
        (lily, post_emma, "The street art scene there is amazing."),
        (sophia, post_alex, "Adding this place to my list for Tokyo!"),
        (emma, post_alex, "I love ramen so much. Looks incredible."),
        (emma, post_lily, "Scotland is so beautiful. Need to visit!"),
        (ryan, post_lily, "The mist makes it look magical."),
        (alex, post_sophia, "Prague is such an underrated city."),
        (lily, post_sophia, "Like stepping into a fairytale indeed!"),
    ]
    for user, post, text in comments_data:
        Comment.objects.get_or_create(user=user, post=post, text=text)
    print(f"  Created {len(comments_data)} comments")

    # --- Bookmarks ---
    bookmark_pairs = [
        (emma, post_alex),
        (emma, post_lily),
        (sophia, post_ryan),
        (sophia, post_lily),
        (ryan, post_lily),
        (alex, post_ryan),
        (alex, post_sophia),
        (lily, post_emma),
    ]
    for user, post in bookmark_pairs:
        Bookmark.objects.get_or_create(user=user, post=post)
    print(f"  Created {len(bookmark_pairs)} bookmarks")

    print("\nPopulation complete!")
    print("You can log in with any user (password: testpass123):")
    for u in created_users:
        print(f"  - {u.username}")


if __name__ == "__main__":
    populate()
