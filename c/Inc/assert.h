#ifndef ASSERT_H
#define ASSERT_H

 /** NASSERT macro disables all contract validations
  * (assertions, preconditions, postconditions, and invariants).
  */
 #ifdef NASSERT           /* NASSERT defined--DbC disabled */
  #define DEFINE_THIS_FILE
 #define ASSERT(ignore_)  ((void)0)
 #define ALLEGE(test_)    ((void)(test_))

 #else                    /* NASSERT not defined--DbC enabled */

 #ifdef __cplusplus
 extern "C"
 {
 #endif
    /* callback invoked in case of assertion failure */
extern void v__OnAssert__(char const *file, unsigned line);
 #ifdef __cplusplus
 }
 #endif

 #define ASSERT_THIS_FILE \
    static char const THIS_FILE__[] = __FILE__;

 #define ASSERT(test_) \
    ((test_) ? (void)0 : v__OnAssert__(THIS_FILE__, __LINE__))

 #define ALLEGE(test_)    ASSERT(test_)

 #endif                   /* NASSERT */

 #define REQUIRE(test_)   ASSERT(test_)
 #define ENSURE(test_)    ASSERT(test_)
 #define INVARIANT(test_) ASSERT(test_)

 ASSERT_THIS_FILE

#endif