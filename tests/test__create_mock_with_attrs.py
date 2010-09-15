from ut_utils import ForgeTestCase
from forge.class_mock import ClassMockObject

class A(object):
    pass
class B(object):
    pass
class C:
    pass
class D(object):
    pass
class E(object):
    pass

class AttrMockTest(ForgeTestCase):
    def test__create_mock_with_attrs(self):
        M = self.forge.create_mock_with_attrs
        result = M(A,
                   b=M(B,
                       c=M(C, d=M(D)),
                       e=M(E),
                  )
              )
        self.assertIsInstanceMockOf(result, A)
        self.assertIsInstanceMockOf(result.b, B)
        self.assertIsInstanceMockOf(result.b.c, C)
        self.assertIsInstanceMockOf(result.b.c.d, D)
        self.assertIsInstanceMockOf(result.b.e, E)

    def assertIsInstanceMockOf(self, obj, cls):
        self.assertIsInstance(obj, ClassMockObject)
        self.assertTrue(obj.__forge__.behaves_as_instance)
        self.assertIs(obj.__forge__.mocked_class, cls)

