# CSE312_666
cupid-666.me

Welcome to CUPID, a modern dating website designed to help people find meaningful connections and build romantic relationships. This README file provides an overview of the project.


Project part 3 additional feature testing procedure:

1. Start your server using docker compose up
2. Open two browsers and navigate to http://localhost:8080/
3. Create an account and login
4. Navigate to explore on the top of right hand side
5. Make 2 posts with unique title, but exists some common substring
    1. ei. Title abc and title bcd
6. Make another post that had no common substring title as the 2 previous posts made
7.     1. ei. Title abc and title def
8. Verify all posts are shown in the explore
9. Enter a common substring of only two of the posts 
    1. ei. Title abc and title bcd has common substring bc
10. Click Search
11. Verify that only the two posts are displayed
12. Click Clear
13. Make sure all posts are displayed
14. Now enter a substring of the post title made in step 6 into search bar
15. Click search
16. Make sure only post made in step 6 is showing
17. Click Clear
18. Make sure all three posts are showing
19. Make another post with no common substring title of the all three posts made above
20. Verify step 8 to 15 again
21. Clear search again
22. Make sure all four posts are showing
23. Now enter each post’s full title in the search bar once at a time and hit clear after each search
24. Make sure only the post that matches the exact title shows

Security: make sure user input search string is HTML escaped

