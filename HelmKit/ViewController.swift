  //
//  ViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/13/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import UIKit
import CoreLocation
import CoreMotion
import SceneKit

class ViewController: UIViewController {

    @IBOutlet weak var eventPanel: EventPanelView!
    @IBOutlet weak var planetProgressionPanel: PlanetProgressionPanelView!
    
    @IBOutlet weak var progressViewMercury: UIProgressView!
    @IBOutlet weak var progressViewVenus: UIProgressView!
    @IBOutlet weak var progressViewEarth: UIProgressView!
    @IBOutlet weak var progressViewMars: UIProgressView!
    @IBOutlet weak var progressViewJupiter: UIProgressView!
    @IBOutlet weak var progressViewSaturn: UIProgressView!
    @IBOutlet weak var progressViewUranus: UIProgressView!
    @IBOutlet weak var progressViewNeptune: UIProgressView!
    
    @IBOutlet weak var mhdSensorSceneView: SCNView!
    var mhdScene:MHDSensorScene {
        return mhdSensorSceneView.scene as! MHDSensorScene
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        mhdSensorSceneView.scene = MHDSensorScene.create()
        mhdSensorSceneView.backgroundColor = UIColor.clear
        mhdSensorSceneView.pointOfView = mhdScene.mainCamera
        
        mhdScene.sphere(.smooth).isHidden = false
        mhdScene.sphere(.ripple).isHidden = true
        mhdScene.sphere(.smoothChaos).isHidden = true
        mhdScene.sphere(.rippleChaos).isHidden = true
        mhdScene.sphere(.strongChaos).isHidden = true
        
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
    }

}
