from setuptools import setup


def readme():
      with open('README.md') as f:
            return f.read()


setup(name='charlotte_traffic_analysis',
      version='0.1.3',
      description='Charlotte-metro traffic analysis helper including predictions, travel paths, and more',
      long_description=readme(),
      long_description_content_type='text/markdown',
      author='Dillon Mabry',
      url='https://github.com/dillonmabry/cmpd-traffic-helper',
      author_email='rapid.dev.solutions@gmail.com',
      license='MIT',
      packages=['cmpd_accidents', 'traffic_analyzer'],
      test_suite='nose.collector',
      tests_require=['nose'],
      # Shapely for Windows requires local pip install # https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
      install_requires=['pymongo', 'requests', 'lxml', 'bs4', 'sqlalchemy',
                        'pymysql', 'numpy', 'pandas', 'scikit-learn', 'xgboost',
                        'shapely', 'matplotlib', 'google-api-python-client'],
      include_package_data=True,
      data_files=[('', [
          'cmpd_accidents/resources/db/mysql_create_accidents.sql',
          'traffic_analyzer/resources/reference_data/census_population.csv',
          'traffic_analyzer/resources/reference_data/roads.csv',
          'traffic_analyzer/resources/reference_data/signals.csv',
          'traffic_analyzer/resources/reference_data/traffic_volumes.csv',
          'traffic_analyzer/resources/models/xgb_cv_optimal_v1.joblib',
          'traffic_analyzer/resources/models/xgb_cv_optimal_v2.joblib'
      ])],
      zip_safe=False)
