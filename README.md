# CSE312_666
cupid-666.me

Welcome to CUPID, a modern dating website designed to help people find meaningful connections and build romantic relationships. This README file provides an overview of the project.


Project part 3 additional feature testing procedure:

1. Start your server using docker compose up
2. Open two browsers and navigate to http://localhost:8080/
3. Create an account and login in both browsers
4. Navigate to explore on the top of right hand side
5. Make 2 posts with unique title, but exists some common substring
    1. ei. Title abc and title bcd
6. Make another post that had no common substring title as the 2 previous posts made in either browser
    1. ei. Title efg
7. Refresh both browsers and verify all posts are shown in the explore
8. Enter a common substring of only two of the posts on top of the browser
    1. ei. Title abc and title bcd has common substring bc
9. Click Search
10. Verify that only the two posts that had the words in it are displayed
11. Click Clear
12. Make sure all posts are displayed
13. Now enter a substring of the post title made in step 6 into search bar
14. Click search
15. Make sure only post made in step 6 is showing
16. Click Clear
17. Make sure all three posts are showing
